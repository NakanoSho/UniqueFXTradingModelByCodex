"""Backward-compatible wrapper for run_vol_daily."""

from __future__ import annotations

from data_pipeline.pipeline.run_vol_daily import main


if __name__ == "__main__":
    raise SystemExit(main())
