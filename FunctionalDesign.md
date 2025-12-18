# Functional Design (Vibe Coding Root)

## 0. Meta
- Project Name: UniqueFXTradingModelByCodex
- Document Role: Source of truth for scope, behavior, and constraints
- Last Updated: 2025-12-18

## 1. Problem Statement
We will design and implement a unique FX trading model. The system should support research, backtesting, and (optionally) paper/live execution with auditable risk controls.

## 2. Goals (MVP)
- Ingest historical FX price data for configurable symbols/timeframes.
- Generate trading signals from a defined strategy logic.
- Run backtests with realistic assumptions (spread, slippage, fees).
- Report performance metrics and trade logs.
- Keep the architecture modular to allow rapid iteration.

## 3. Non-Goals (Initial Scope)
- No direct real-money execution in the initial MVP.
- No complex ML training pipelines in the first iteration.
- No GUI; CLI or simple script-driven workflow is sufficient.

## 4. Users & Use Cases
- Quant/Researcher: iterate on strategy logic and evaluate results.
- Developer: extend data sources, add indicators, refactor components.

## 5. Functional Requirements
### 5.1 Data
- Support OHLCV time series for FX pairs.
- Data source should be swappable (CSV, API, broker export).
- Timezone handling must be consistent and explicit.

### 5.2 Strategy
- Strategy interface should accept market data and output signals.
- Signals must be timestamped and comparable to price bars.
- Strategy parameters should be configurable (e.g., via config file).

### 5.3 Backtesting
- Event-driven or vectorized backtest engine is acceptable if results are deterministic.
- Include spreads, slippage, and commission models.
- Produce trades, equity curve, and summary stats.

### 5.4 Risk & Positioning
- Position sizing strategy should be pluggable.
- Enforce max drawdown or exposure constraints where applicable.

### 5.5 Reporting
- Output summary metrics: CAGR, Sharpe, Max Drawdown, Win Rate, Profit Factor.
- Export trade list and equity curve to files.

## 6. System Constraints
- Deterministic results with fixed inputs.
- Reproducible runs with pinned parameters.
- Clear separation of data, strategy, execution, and reporting.

## 7. Architecture (Initial)
- data/: loaders and adapters
- strategy/: signal generation
- backtest/: engine and execution model
- risk/: sizing and constraints
- report/: metrics and exports
- config/: parameters and presets
- notebooks/ or scripts/: experiments

## 8. Interfaces
- CLI entry point to run backtest and output results.
- Config file (YAML or TOML) to define symbols, timeframe, and strategy params.

## 9. Assumptions
- Data quality is sufficient for research; missing bars will be handled.
- All times are normalized to UTC internally.

## 10. Milestones
1) Project skeleton + minimal backtest loop
2) Strategy v1 + baseline metrics
3) Parameterization + reporting exports

## 11. Open Questions
- Preferred data source and symbol universe?
- Execution mode for future (paper vs live)?
- Desired timeframes for initial experiments?

