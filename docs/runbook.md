# Trading Operations Runbook

## Purpose
This runbook provides preflight, deployment, monitoring, and rollback procedures for the options trading platform across paper and live modes.

## Preflight Checklist
1. Export environment variables (`OPENALGO_API_KEY`, `OPENALGO_HOST`, `TRADING_MODE`).
2. Install dependencies: `python -m pip install -r requirements.txt`.
3. Execute local smoke tests: `python -m pytest`.
4. Run deployment checks: `python scripts/deploy_service.py --mode paper` (or `--mode live`).
5. Confirm broker connectivity and available margin in the deployment script output.

## Deployment Steps
### Paper Trading
1. Run `python scripts/paper_trading_loop.py` in a long-lived terminal session or supervisor.
2. Verify log output in `logs/app.log` for feed subscription and strategy execution events.

### Live Trading
1. Ensure `TRADING_MODE=live` and production credentials are loaded.
2. Execute `python scripts/deploy_service.py --mode live` and confirm all checks pass.
3. Launch the live loop (or orchestrator) with appropriate process management tooling.
4. Enable alerting hooks (Slack/email) for risk excursions if available.

## Monitoring
- Tail `logs/app.log` for order flow, risk controller decisions, and feed events.
- Track portfolio greeks and margin utilisation via the periodic snapshots emitted by `RiskController`.
- Review QuantStats HTML reports generated in the configured `report_dir` for post-session analysis.

## Troubleshooting
| Issue | Resolution |
| ----- | ---------- |
| Feed connection failures | Re-run `deploy_service.py` to validate connectivity, fall back to REST polling if necessary. |
| Risk gate rejects orders | Inspect logs for the violating constraint, adjust limits in `config/settings.py` if appropriate. |
| QuantStats report missing | Confirm `report_dir` exists and that the CI run installed `quantstats`; rerun the backtest with the directory writeable. |

## Shutdown
1. For graceful exit, send `SIGINT` to the trading loop; ensure logs show feed unsubscription.
2. Confirm open positions are reconciled via `PositionTracker.as_dict()` or broker dashboard.
3. Archive daily reports and logs for audit.
