## Operational Workflows

### Running Paper Trading Scripts
- **Deployment preflight**: `python scripts/deploy_service.py --mode paper|live`
  - Validates environment variables, fetches broker funds, and sanity-checks websocket connectivity.
- **Synchronous demo**: `python scripts/run_paper_trading.py`
  - Initializes `StrategyManager`, `RiskController`, and mocked broker services.
  - Subscribes to LTP feeds when available and logs approved orders.
- **Asynchronous loop**: `python scripts/paper_trading_loop.py`
  - Continuously polls market data through `MarketDataService` while consuming websocket price updates.
  - Refreshes portfolio exposures and submits signals while respecting risk gates.

### Integrating with Live Brokers
1. Populate `.env` with production keys and set `TRADING_MODE=live`.
2. Extend or swap adapter hooks in `OpenAlgoClient` if additional broker APIs or custom payload tweaks are required.
3. Replace mock margin/positions providers with real endpoints when instantiating `MarginMonitor` and `PositionTracker`.
4. Subscribe to feed callbacks (LTP/quotes/depth) via the adapter helpers or fall back to REST polling.
5. Monitor trade logs produced by `TradeLogger` for auditing.

### Risk Management Lifecycle
1. **StrategyManager** requests fresh context from `MarketDataService`.
2. Strategies emit `Signal` objects describing desired trades.
3. **RiskController** validates portfolio VaR, margin buffers, and greek limits.
4. Approved signals pass to `OrderManager` for execution; rejected signals are logged for review.
5. **PositionTracker** updates positions to keep exposures synchronized.

### Monitoring & Logging
- Logs default to rotating files via loguru configuration in `src/utils/logger.py`.
- Customize sink destinations or verbosity through the logger setup before initializing managers.
- Use `TradeLogger` output for compliance, and integrate with external observability stacks as needed.
- Capture feed heartbeat/latency metrics via callbacks to ensure websocket health.

### Scheduling & Automation
- Trigger scripts via cron/Windows Task Scheduler, ensuring environment variables exist in the runtime context.
- For long-running services, wrap scripts with process managers (e.g., `systemd`, `supervisord`).
- Leverage the GitHub Actions CI pipeline to enforce lint/type/test gates before deployments.

### Extending Strategies
1. Derive a new class from `BaseStrategy`.
2. Implement `build_signals` using helpers from `OptionsChainHandler` and configuration defaults.
3. Register the strategy instance with `StrategyManager` alongside existing strategies.
4. Add targeted unit tests under `tests/test_strategies/` to validate expected behaviors.

### Backtesting
- Configure strategy parameters in `config/strategy_config.py`.
- Use `BacktestRunner` from `src/backtesting/backtest_runner.py` within notebooks or scripts to replay scenarios.
- Generate QuantStats tear sheets via `BacktestRunner.build_report` or `build_backtest_report` for post-trade analysis.
- Archive HTML/CSV outputs for audit using the configured report directory.
