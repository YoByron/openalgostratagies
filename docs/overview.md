## Project Overview

OpenAlgo Options Platform is an institutional-grade framework for building, testing, and deploying multi-leg options strategies on Indian indices. The codebase layers reusable abstractions on top of OpenAlgo for execution and market data while pairing them with advanced risk controls, strategy orchestration, and backtesting utilities.

### Core Capabilities
- Unified configuration via Pydantic settings and strategy profiles.
- Broker-agnostic data and execution access through the `OpenAlgoClient` wrapper backed by the official `openalgo` SDK adapter.
- Modular strategy library covering delta-neutral, spreads, and income strategies.
- Portfolio-level Greeks calculation and risk gating with configurable thresholds.
- Execution management with order lifecycle control, trade logging, and position tracking.
- VectorBT-powered backtesting with QuantStats HTML/CSV reporting helpers for tear sheets.
- Websocket-enabled market data feeds powering paper trading loops and scenario-driven tests.
- GitHub Actions CI enforcing Ruff, mypy, and pytest runs for continuous quality.

### Key Directories
- `config/` – Environment settings and strategy configuration models.
- `src/data/` – Market data services, options chain processing, and OpenAlgo client.
- `src/strategies/` – Base strategy abstractions and concrete strategy implementations.
- `src/risk/` – Position sizing, margin and VaR monitors, limits checker, risk controller.
- `src/greeks/` – Option pricing and portfolio Greeks aggregation utilities.
- `src/execution/` – Order manager, position tracker, trade logger.
- `src/backtesting/` – VectorBT integration and performance metrics orchestration.
- `src/utils/` – Logging configuration, validation helpers, and shared utilities.
- `scripts/` – Paper trading workflows and orchestration scripts.
- `tests/` – Unit and integration tests spanning strategies, risk, data, and backtesting.

### Architecture at a Glance
1. **Configuration Layer** loads environment secrets, risk limits, and strategy parameters.
2. **Data Layer** adapts OpenAlgo REST endpoints while enriching option chains with analytics.
3. **Strategy Layer** produces trade intents constrained by base abstractions and configuration.
4. **Risk Layer** evaluates VaR, margin, limits, and position sizing prior to execution approval.
5. **Execution Layer** handles order submission, tracking, and logging with broker abstractions.
6. **Backtesting Layer** replays strategies with VectorBT and compiles analytics for review.
7. **Testing Layer** validates components with deterministic fixtures and scenario coverage.

Refer to `architecture.md` for deeper module-level explanations and component diagrams.
