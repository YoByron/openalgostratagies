"""Order management integrating with OpenAlgo."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from loguru import logger

from config.settings import settings
from src.data.openalgo_client import openalgo


@dataclass(slots=True)
class OrderRequest:
    symbol: str
    exchange: str
    action: str
    quantity: int
    price: float
    product: str = "MIS"
    order_type: str = "LIMIT"
    validity: str = "DAY"
    disclosed_quantity: int = 0
    trigger_price: Optional[float] = None


class OrderManager:
    """Handles order lifecycle and abstracts OpenAlgo calls."""

    def __init__(self) -> None:
        self.default_exchange = settings.EXCHANGE

    def submit_order(self, request: OrderRequest) -> Dict[str, Any]:
        payload = request.__dict__.copy()
        logger.debug("Submitting order", **payload)
        response = openalgo.place_order(**payload)
        logger.info("Order submitted", order_id=response.get("order_id"))
        return response

    def modify_order(self, order_id: str, quantity: Optional[int] = None, price: Optional[float] = None) -> Dict[str, Any]:
        logger.debug("Modifying order", order_id=order_id, quantity=quantity, price=price)
        response = openalgo.modify_order(order_id, quantity=quantity, price=price)
        logger.info("Order modified", order_id=order_id)
        return response

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        logger.debug("Cancelling order", order_id=order_id)
        response = openalgo.cancel_order(order_id)
        logger.info("Order cancelled", order_id=order_id)
        return response

    def close_position(self, symbol: str, exchange: Optional[str] = None, product: str = "MIS") -> Dict[str, Any]:
        target_exchange = exchange or self.default_exchange
        logger.debug("Closing position", symbol=symbol, exchange=target_exchange, product=product)
        response = openalgo.close_position(symbol, target_exchange, product)
        logger.info("Position close requested", symbol=symbol)
        return response

    def fetch_order_book(self) -> Dict[str, Any]:
        return {"orders": openalgo.get_order_book()}

    def fetch_positions(self) -> Dict[str, Any]:
        return {"positions": openalgo.get_positions()}

    def fetch_funds(self) -> Dict[str, Any]:
        return openalgo.get_funds()
