"""OpenAlgo API client wrapper using the official SDK adapter."""
from typing import Any, Dict, List, Optional

from config.settings import settings
from src.data.openalgo_adapter import OpenAlgoSDKAdapter


class OpenAlgoClient:
    """Thin wrapper delegating to the OpenAlgo SDK adapter."""

    def __init__(self) -> None:
        self._adapter = OpenAlgoSDKAdapter(
            api_key=settings.OPENALGO_API_KEY,
            host=settings.OPENALGO_HOST,
        )

    def get_quotes(self, symbol: str, exchange: str = "NFO") -> Dict[str, Any]:
        return self._adapter.get_quotes(symbol, exchange)

    def get_option_chain(self, symbol: str, expiry: str) -> List[Dict[str, Any]]:
        return self._adapter.get_option_chain(symbol, expiry)

    def get_depth(self, symbol: str, exchange: str = "NFO") -> Dict[str, Any]:
        return self._adapter.get_depth(symbol, exchange)

    def place_order(
        self,
        symbol: str,
        exchange: str,
        action: str,
        quantity: int,
        price: float,
        product: str = "MIS",
        order_type: str = "LIMIT",
        disclosed_quantity: Optional[int] = None,
        trigger_price: Optional[float] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        return self._adapter.place_order(
            symbol=symbol,
            exchange=exchange,
            action=action,
            quantity=quantity,
            price=price,
            product=product,
            order_type=order_type,
            disclosed_quantity=disclosed_quantity,
            trigger_price=trigger_price,
            **kwargs,
        )

    def modify_order(
        self,
        order_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        return self._adapter.modify_order(order_id, quantity=quantity, price=price)

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        return self._adapter.cancel_order(order_id)

    def get_order_book(self) -> List[Dict[str, Any]]:
        return self._adapter.get_order_book()

    def get_positions(self) -> List[Dict[str, Any]]:
        return self._adapter.get_positions()

    def get_holdings(self) -> List[Dict[str, Any]]:
        return self._adapter.get_holdings()

    def close_position(
        self,
        symbol: str,
        exchange: str,
        product: str = "MIS",
    ) -> Dict[str, Any]:
        return self._adapter.close_position(symbol, exchange, product)

    def get_funds(self) -> Dict[str, Any]:
        return self._adapter.get_funds()

    def get_margins(self, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._adapter.get_margins(positions)

    def cancel_all_orders(self) -> Dict[str, Any]:
        return self._adapter.cancel_all_orders()

    def connect_feed(self) -> bool:
        return self._adapter.connect_feed()

    def disconnect_feed(self) -> None:
        self._adapter.disconnect_feed()

    def subscribe_ltp(self, instruments: List[Dict[str, Any]], callback: Optional[Any] = None) -> bool:
        return self._adapter.subscribe_ltp(instruments, callback)

    def unsubscribe_ltp(self, instruments: List[Dict[str, Any]]) -> bool:
        return self._adapter.unsubscribe_ltp(instruments)

    def subscribe_quote(self, instruments: List[Dict[str, Any]], callback: Optional[Any] = None) -> bool:
        return self._adapter.subscribe_quote(instruments, callback)

    def unsubscribe_quote(self, instruments: List[Dict[str, Any]]) -> bool:
        return self._adapter.unsubscribe_quote(instruments)

    def subscribe_depth(self, instruments: List[Dict[str, Any]], callback: Optional[Any] = None) -> bool:
        return self._adapter.subscribe_depth(instruments, callback)

    def unsubscribe_depth(self, instruments: List[Dict[str, Any]]) -> bool:
        return self._adapter.unsubscribe_depth(instruments)

    def get_ltp_snapshot(self, exchange: Optional[str] = None, symbol: Optional[str] = None) -> Dict[str, Any]:
        return self._adapter.get_ltp_snapshot(exchange, symbol)

    def get_quote_snapshot(self, exchange: Optional[str] = None, symbol: Optional[str] = None) -> Dict[str, Any]:
        return self._adapter.get_quote_snapshot(exchange, symbol)

    def get_depth_snapshot(self, exchange: Optional[str] = None, symbol: Optional[str] = None) -> Dict[str, Any]:
        return self._adapter.get_depth_snapshot(exchange, symbol)


openalgo = OpenAlgoClient()
