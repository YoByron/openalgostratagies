"""Example paper trading loop with integrated risk controls."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger

from config.settings import settings
from src.data.market_data_service import MarketDataService
from src.data.openalgo_client import openalgo
from src.execution.order_manager import OrderManager
from src.execution.position_tracker import PositionTracker
from src.risk.margin_monitor import MarginMonitor
from src.risk.risk_controller import RiskController
from src.strategies.iron_condor import IronCondorStrategy
from src.strategies.strategy_manager import StrategyManager
from src.strategies.base_strategy import Signal
from src.utils.logger import configure_logging


def build_demo_signal() -> Signal:
    legs = [
        {"action": "SELL", "strike": 20000, "option_type": "CE", "quantity": 1, "price": 150.0},
        {"action": "BUY", "strike": 20200, "option_type": "CE", "quantity": 1, "price": 60.0},
        {"action": "SELL", "strike": 20000, "option_type": "PE", "quantity": 1, "price": 140.0},
        {"action": "BUY", "strike": 19800, "option_type": "PE", "quantity": 1, "price": 55.0},
    ]
    return Signal(
        action="ENTER",
        legs=legs,
        reason="Demo Iron Condor entry",
        timestamp=datetime.now(),
        metadata={"symbol": settings.SYMBOL},
    )


def main() -> None:
    configure_logging()

    def extract_ltp(message: Dict[str, Any]) -> Optional[float]:
        if not isinstance(message, dict):
            return None
        if "ltp" in message and isinstance(message["ltp"], (int, float)):
            return float(message["ltp"])
        data = message.get("data")
        if isinstance(data, dict) and "ltp" in data and isinstance(data["ltp"], (int, float)):
            return float(data["ltp"])
        return None

    order_manager = OrderManager()
    position_tracker = PositionTracker()

    margin_monitor = MarginMonitor(
        max_utilization_pct=0.7,
        margin_fetcher=lambda positions: {"span_margin": 20_000},
        funds_fetcher=lambda: {"available_margin": 500_000},
    )

    risk_controller = RiskController(
        portfolio_value=1_000_000,
        margin_monitor=margin_monitor,
    )

    market_data_service = MarketDataService(symbol=settings.SYMBOL, exchange=settings.EXCHANGE)

    manager = StrategyManager(
        order_manager=order_manager,
        position_tracker=position_tracker,
        risk_controller=risk_controller,
        market_data_service=market_data_service,
        execution_mode="dry_run",
    )

    strategy = IronCondorStrategy()
    manager.register_strategy(strategy)

    latest_ltp: Dict[str, Optional[float]] = {"ltp": None}
    feed_instruments = [{"exchange": settings.EXCHANGE, "symbol": settings.SYMBOL}]
    feed_active = False

    try:
        feed_active = openalgo.connect_feed()
        if feed_active:
            openalgo.subscribe_ltp(feed_instruments, callback=lambda msg: latest_ltp.update({"ltp": extract_ltp(msg)}))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Unable to subscribe to LTP feed", error=str(exc))
        feed_active = False

    signal = build_demo_signal()

    spot_price = market_data_service.fetch_spot_price()
    if latest_ltp["ltp"] is not None:
        spot_price = latest_ltp["ltp"]

    market_data = {
        "portfolio_value": 1_000_000,
        "returns": 0.001,
        "portfolio_greeks": {"delta": 25.0, "gamma": 10.0, "vega": 200.0},
        "estimated_margin": 15_000,
        "leg_symbols": {
            ("CE", 20000, None): "NIFTY24JUL20000CE",
            ("CE", 20200, None): "NIFTY24JUL20200CE",
            ("PE", 20000, None): "NIFTY24JUL20000PE",
            ("PE", 19800, None): "NIFTY24JUL19800PE",
        },
        "leg_prices": {
            ("CE", 20000, None): 150.0,
            ("CE", 20200, None): 60.0,
            ("PE", 20000, None): 140.0,
            ("PE", 19800, None): 55.0,
        },
        "signals": {strategy.name: signal},
        "skip_market_refresh": True,
        "spot_price": spot_price,
    }

    manager.process_market_data(market_data)

    if feed_active:
        try:
            openalgo.unsubscribe_ltp(feed_instruments)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to unsubscribe demo feed", error=str(exc))
        openalgo.disconnect_feed()


if __name__ == "__main__":
    main()
