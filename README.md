# OpenAlgo Options Platform

Institutional-grade framework for building, risk-managing, and deploying multi-leg options strategies on Indian indices using OpenAlgo for execution and data.

## Features
- Broker abstraction via `OpenAlgoClient`, powered by the official `openalgo` SDK adapter, now with websocket helpers for real-time LTP/quote/depth feeds.
- Pluggable strategy layer with base abstractions and ready-to-use strategies (Iron Condor, Straddle, Strangle, Butterfly, Calendar Spread, Delta Neutral).
- Comprehensive risk stack covering VaR, margin monitoring, position sizing, stop losses, and greek-based exposure limits.
- Execution management with order lifecycle control, position tracking, and structured trade logging.
- Backtesting toolkit powered by VectorBT plus QuantStats-based HTML/CSV reporting utilities.
- Paper-trading scripts with live feed ingestion, scenario/integration tests, and GitHub Actions CI (pytest, Ruff, mypy) for safe validation before live deployment.

## Quick Start
1. **Set up environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate # macOS/Linux
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
2. **Configure credentials**
   - Copy `.env.example` to `.env` and populate OpenAlgo keys plus risk settings.
   - Adjust strategy profiles in `config/strategy_config.py` as needed.
3. **Verify setup**
   ```bash
   python -m pytest
   ```
4. **Run deployment checks (optional)**
   ```bash
   python scripts/deploy_service.py --mode paper
   ```

## Usage
- **Deployment preflight**: `python scripts/deploy_service.py --mode paper|live`
- **Paper trading demo**: `python scripts/run_paper_trading.py`
- **Async trading loop**: `python scripts/paper_trading_loop.py`
- **Backtesting**: import `BacktestRunner` / `BacktestReport` helpers from `src/backtesting/backtest_runner.py` and `src/backtesting/reporting.py` (see `notebooks/backtest_quickstart.ipynb`).

## Project Layout
- `config/` – Environment settings and strategy defaults.
- `src/data/` – OpenAlgo SDK adapter/client, options chain utilities, market data service.
- `src/strategies/` – Base strategy abstractions and concrete strategies.
- `src/risk/` – Position sizing, risk limits, VaR, margin, stop loss, risk controller.
- `src/execution/` – Order manager, position tracker, trade logger.
- `src/backtesting/` – VectorBT integration and performance reporting.
- `src/greeks/` – Greeks calculator and portfolio aggregation.
- `scripts/` – Operational entry points for paper trading workflows and deployment checks.
- `tests/` – Unit and integration coverage for strategies, risk, data, and backtesting.
- `notebooks/` – Interactive analyses, including `backtest_quickstart.ipynb` demonstrating report generation.
- `.github/` – CI workflow running lint, type checks, and pytest.

## Documentation
Detailed guides live under `docs/`:
- [Overview](docs/overview.md)
- [Setup](docs/setup.md)
- [Architecture](docs/architecture.md)
- [Operations](docs/operations.md)
- [Testing](docs/testing.md)
- [Runbook](docs/runbook.md)

## Optional Enhancements
- Install `vectorbt`, `quantstats`, `riskfolio-lib`, or `ta-lib` for advanced analytics.
- Explore the CI workflow under `.github/workflows/ci.yml` to customize quality gates.
- Extend strategies by inheriting from `BaseStrategy` and registering with `StrategyManager`.
- Use the deployment runbook (`docs/runbook.md`) for operational handoffs.

## Disclaimer
This repository is for educational purposes. Validate strategies with appropriate risk controls before deploying capital.
