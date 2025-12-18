"""Build daily bars from tick data."""

from __future__ import annotations

from datetime import datetime, time, timezone
from typing import Dict, Iterable, List, Tuple


def _parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _date_str(dt: datetime) -> str:
    return dt.date().isoformat()


def _quantile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    values_sorted = sorted(values)
    idx = int(round((len(values_sorted) - 1) * q))
    return values_sorted[idx]


def ticks_to_daily_bars(
    ticks: Iterable[Dict[str, object]],
    close_time_utc: str,
    only_date: str | None = None,
) -> List[Dict[str, object]]:
    close_parts = [int(x) for x in close_time_utc.split(":"))
    close_t = time(close_parts[0], close_parts[1], close_parts[2])
    grouped: Dict[Tuple[str, str], List[Dict[str, object]]] = {}
    for row in ticks:
        ts = _parse_ts(str(row["ts"]))
        date_key = _date_str(ts)
        if only_date is not None and date_key != only_date:
            continue
        pair = str(row["pair"])
        grouped.setdefault((pair, date_key), []).append({**row, "_ts": ts})

    bars: List[Dict[str, object]] = []
    for (pair, date_key), rows in grouped.items():
        rows_sorted = sorted(rows, key=lambda r: r["_ts"])
        close_cutoff = datetime.combine(rows_sorted[0]["_ts"].date(), close_t, tzinfo=timezone.utc)
        before_close = [r for r in rows_sorted if r["_ts"] <= close_cutoff]
        close_row = before_close[-1] if before_close else rows_sorted[-1]
        missing_close = not bool(before_close)
        spreads = [float(r.get("spread_bps") or 0.0) for r in rows_sorted]
        bar = {
            "date": date_key,
            "pair": pair,
            "daily_close_mid": float(close_row["mid"]),
            "daily_close_bid": float(close_row["bid"]),
            "daily_close_ask": float(close_row["ask"]),
            "close_ts": close_row["_ts"].isoformat().replace("+00:00", "Z"),
            "spread_bps_median": _quantile(spreads, 0.5),
            "spread_bps_p95": _quantile(spreads, 0.95),
            "tick_count": len(rows_sorted),
            "missing_close": missing_close,
        }
        bars.append(bar)
    return bars
