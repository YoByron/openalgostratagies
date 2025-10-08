"""Async paper trading loop integrating real-time market data and risk checks."""
from __future__ import annotations

import asyncio
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
from src.utils.logger import configure_logging


POLL_INTERVAL_SECONDS = 5


def _extract_ltp(message: Dict[str, Any]) -> Optional[float]:
    if not isinstance(message, dict):
        return None
    if "ltp" in message and isinstance(message["ltp"], (int, float)):
        return float(message["ltp"])
    data = message.get("data")
    if isinstance(data, dict) and "ltp" in data and isinstance(data["ltp"], (int, float)):
        return float(data["ltp"])
    return None


async def main() -> None:
    configure_logging()

    position_tracker = PositionTracker()
    order_manager = OrderManager()
    market_data_service = MarketDataService(symbol=settings.SYMBOL, exchange=settings.EXCHANGE)

    margin_monitor = MarginMonitor()
    risk_controller = RiskController(
        portfolio_value=1_000_000,
        margin_monitor=margin_monitor,
    )

    manager = StrategyManager(
        order_manager=order_manager,
        position_tracker=position_tracker,
        risk_controller=risk_controller,
        market_data_service=market_data_service,
        execution_mode="paper",
    )

    manager.register_strategy(IronCondorStrategy(settings.SYMBOL))

    feed_instruments = [{"exchange": settings.EXCHANGE, "symbol": settings.SYMBOL}]
    latest_feed = {"ltp": None}
    feed_active = False

    def handle_ltp(message: Dict[str, Any]) -> None:
        price = _extract_ltp(message)
        if price is not None:
            latest_feed["ltp"] = price

    try:
        feed_active = openalgo.connect_feed()
        if feed_active:
            openalgo.subscribe_ltp(feed_instruments, callback=handle_ltp)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Unable to initialize market data feed", error=str(exc))
        feed_active = False

    try:
        while True:
            try:
                broker_positions = openalgo.get_positions()
                position_tracker.sync_from_broker(broker_positions)

                snapshot = market_data_service.snapshot([pos.as_dict() for pos in position_tracker.all_positions()])
                effective_spot = latest_feed["ltp"] if latest_feed["ltp"] is not None else snapshot.spot_price
                returns = snapshot.portfolio_greeks.get("delta", 0.0) / 1000

                market_context = {
                    "portfolio_value": risk_controller.portfolio_value,
                    "returns": returns,
                    "estimated_margin": 0.0,
                    "timestamp": snapshot.timestamp,
                    "skip_market_refresh": True,
                    "portfolio_greeks": snapshot.portfolio_greeks,
                    "spot_price": effective_spot,
                }

                manager.process_market_data(market_context)
            except Exception as exc:  # noqa: BLE001
                logger.error("Paper trading loop error", error=str(exc))

            await asyncio.sleep(POLL_INTERVAL_SECONDS)
    finally:
        if feed_active:
            try:
                openalgo.unsubscribe_ltp(feed_instruments)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to unsubscribe from LTP feed", error=str(exc))
            openalgo.disconnect_feed()


if __name__ == "__main__":
    asyncio.run(main())
