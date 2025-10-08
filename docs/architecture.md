## System Architecture

The platform follows a layered design that isolates configuration, data access, strategy logic, risk controls, execution, and analytics. Each layer exposes well-defined interfaces to simplify testing and future broker integrations.

### Configuration Layer
- `config/settings.py` provides a Pydantic settings model (`Settings`) centralizing credentials, risk limits, and feature flags.
- `config/strategy_config.py` defines reusable strategy parameter profiles (e.g., DTE windows, delta targets, lot sizing) consumed by concrete strategies.

### Data Layer
- `src/data/openalgo_adapter.py` bridges the official `openalgo` SDK with project conventions, normalizing payloads and responses.
- `src/data/openalgo_adapter.py` also exposes websocket helpers for LTP/quote/depth subscriptions and snapshots.
- `src/data/openalgo_client.py` exposes the legacy client interface while delegating to the adapter for quotes, chains, orders, positions, margin metadata, and feed connectivity.
- `src/data/options_chain.py` converts raw option chain payloads into normalized structures with ATM identification and delta-based strike selection utilities.
- `src/data/market_data_service.py` orchestrates periodic polling of quotes/chains, generates aggregated Greeks snapshots, and exposes them to strategy orchestration.

### Strategy Layer
- `src/strategies/base_strategy.py` houses:
  - `BaseStrategy` abstract class defining signal generation, entry/exit hooks, and required portfolio context.
  - `Signal` and `Position` dataclasses for normalized representation of trades and holdings.
- Strategy implementations (Iron Condor, Straddle, Strangle, Butterfly, Calendar Spread, Delta Neutral) inherit from `BaseStrategy`, incorporating configuration-driven parameters and utilizing `OptionsChainHandler` helpers.
- `src/strategies/strategy_manager.py` coordinates multiple strategies, refreshes market context through `MarketDataService`, and funnels intents through the risk controller before calling execution services.

### Greeks & Risk Layer
- `src/greeks/calculator.py` computes Black-Scholes greeks and implied volatility using `py_vollib` while supporting custom valuation timestamps.
- `src/greeks/portfolio_greeks.py` aggregates leg-level greeks into portfolio exposures for risk evaluation.
- `src/risk/position_sizer.py` implements fixed-fraction, Kelly, and margin-aware sizing utilities.
- `src/risk/risk_limits.py` enforces configurable delta, gamma, vega, theta, and drawdown thresholds.
- `src/risk/stop_loss.py` provides per-position fixed and trailing stop handling.
- `src/risk/var_calculator.py` offers historical and variance-covariance VaR estimations.
- `src/risk/margin_monitor.py` normalizes broker margin snapshots via dependency-injected fetchers for easier testing.
- `src/risk/risk_controller.py` centralizes approval logic by combining VaR checks, margin availability, risk limits, and recent returns data.

### Execution Layer
- `src/execution/order_manager.py` manages order submission, modification, cancellation, and closing logic against the broker.
- `src/execution/position_tracker.py` syncs broker positions, calculates portfolio metrics, and exposes snapshots for analytics.
- `src/execution/trade_logger.py` configures loguru-based trade journals with rotation and structured payloads.

### Backtesting & Analytics Layer
- `src/backtesting/vectorbt_engine.py` wraps VectorBT to transform strategy signals into executed trades under configurable assumptions.
- `src/backtesting/performance_metrics.py` plugs QuantStats for tear sheets and risk/return analytics.
- `src/backtesting/reporting.py` packages stats, HTML, and CSV exports into reusable report objects.
- `src/backtesting/backtest_runner.py` binds the VectorBT engine, metrics, and reporting layer into a repeatable workflow.

### Utilities & Shared Services
- `src/utils/logger.py` configures global logging with loguru sinks.
- `src/utils/helpers.py` and `src/utils/validators.py` provide common collection utilities, timezone helpers, and input validation.

### Scripts & Workflows
- `scripts/run_paper_trading.py` demonstrates a dry-run execution flow with mocked margin fetchers and live LTP feed integration.
- `scripts/paper_trading_loop.py` showcases an asynchronous paper-trading loop leveraging the market data service, risk gates, and websocket feeds.
- `scripts/deploy_service.py` coordinates preflight checks (env validation, funds lookup, feed connectivity) before launching trading services.

### Testing Strategy
- Unit tests cover greeks computation, risk guards, and strategy logic with deterministic fixtures.
- Integration tests simulate multi-step flows (strategy creation → risk evaluation → execution) using stubbed clients to avoid external calls.
- VectorBT-dependent tests are skipped automatically when the library is absent, ensuring compatibility with lean environments.
