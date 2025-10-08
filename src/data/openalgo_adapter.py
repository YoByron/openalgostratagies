"""Adapter wrapping the official OpenAlgo SDK while preserving legacy interfaces."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

import httpx
from loguru import logger
from openalgo import api as OpenAlgoAPI


class OpenAlgoSDKAdapter:
    """Lightweight facade over the OpenAlgo SDK normalizing responses."""

    def __init__(
        self,
        api_key: str,
        host: str,
        version: str = "v1",
        timeout: float = 10.0,
    ) -> None:
        self._api_key = api_key
        self._host = host.rstrip("/")
        self._timeout = timeout
        self._client = OpenAlgoAPI(api_key=api_key, host=self._host)
        # FeedAPI constructor does not expose timeout keyword, assign manually if available.
        if hasattr(self._client, "timeout"):
            self._client.timeout = timeout
        self._base_url = f"{self._host}/api/{version.strip('/')}/"
        self._feed_connected = False

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _post(self, endpoint: str, payload: Mapping[str, Any]) -> Dict[str, Any]:
        url = f"{self._base_url}{endpoint}"
        data = {"apikey": self._api_key, **payload}
        try:
            response = httpx.post(url, json=data, headers=self._client.headers, timeout=self._timeout)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:  # noqa: PERF203 - we want the exception logged before bubbling up
            logger.error("OpenAlgo SDK adapter request failed", endpoint=endpoint, error=str(exc))
            raise

    @staticmethod
    def _unwrap(response: Any) -> Any:
        if isinstance(response, dict) and "data" in response:
            return response["data"]
        return response

    @staticmethod
    def _normalize_order_payload(order_type: str) -> str:
        mapped = order_type.upper()
        return mapped if mapped in {"MARKET", "LIMIT", "SL", "SL-M"} else "LIMIT"

    @staticmethod
    def _normalize_order_response(response: Dict[str, Any]) -> Dict[str, Any]:
        if "orderid" in response and "order_id" not in response:
            response = {**response, "order_id": response["orderid"]}
        return response

    # ------------------------------------------------------------------
    # Public API used by the legacy client
    # ------------------------------------------------------------------
    def get_quotes(self, symbol: str, exchange: str) -> Dict[str, Any]:
        response = self._client.quotes(symbol=symbol, exchange=exchange)
        return self._unwrap(response) or {}

    def get_option_chain(self, symbol: str, expiry: str) -> List[Dict[str, Any]]:
        response = self._post("optionchain", {"symbol": symbol, "expiry": expiry})
        unwrapped = self._unwrap(response)
        return unwrapped if isinstance(unwrapped, list) else []

    def get_depth(self, symbol: str, exchange: str) -> Dict[str, Any]:
        response = self._client.depth(symbol=symbol, exchange=exchange)
        return self._unwrap(response) or {}

    def place_order(
        self,
        *,
        symbol: str,
        exchange: str,
        action: str,
        quantity: int,
        price: float,
        product: str,
        order_type: str,
        disclosed_quantity: Optional[int] = None,
        trigger_price: Optional[float] = None,
        strategy: str = "Python",
        **extra: Any,
    ) -> Dict[str, Any]:
        price_type = self._normalize_order_payload(order_type)
        kwargs: Dict[str, Any] = {}
        if price_type != "MARKET":
            kwargs["price"] = price
        if disclosed_quantity is not None:
            kwargs["disclosed_quantity"] = disclosed_quantity
        if trigger_price is not None:
            kwargs["trigger_price"] = trigger_price
        kwargs.update({k: v for k, v in extra.items() if v is not None})

        response = self._client.placeorder(
            strategy=strategy,
            symbol=symbol,
            action=action,
            exchange=exchange,
            price_type=price_type,
            product=product,
            quantity=quantity,
            **kwargs,
        )
        if isinstance(response, dict):
            return self._normalize_order_response(response)
        return {"status": "error", "message": "Unexpected response from OpenAlgo"}

    def modify_order(
        self,
        order_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"orderid": order_id}
        if quantity is not None:
            payload["quantity"] = quantity
        if price is not None:
            payload["price"] = price
        response = self._post("modifyorder", payload)
        if isinstance(response, dict):
            return self._normalize_order_response(response)
        return {"status": "error", "message": "Unexpected response from OpenAlgo"}

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        response = self._client.cancelorder(order_id=order_id)
        if isinstance(response, dict):
            return self._normalize_order_response(response)
        return {"status": "error", "message": "Unexpected response from OpenAlgo"}

    def get_order_book(self) -> List[Dict[str, Any]]:
        response = self._client.orderbook()
        unwrapped = self._unwrap(response)
        if isinstance(unwrapped, dict):
            return unwrapped.get("orders", [])
        return unwrapped or []

    def get_positions(self) -> List[Dict[str, Any]]:
        response = self._client.positionbook()
        unwrapped = self._unwrap(response)
        return unwrapped if isinstance(unwrapped, list) else []

    def get_holdings(self) -> List[Dict[str, Any]]:
        response = self._client.holdings()
        unwrapped = self._unwrap(response)
        if isinstance(unwrapped, dict):
            return unwrapped.get("holdings", [])
        return unwrapped if isinstance(unwrapped, list) else []

    def close_position(self, symbol: str, exchange: str, product: str) -> Dict[str, Any]:
        response = self._post(
            "closeposition",
            {"symbol": symbol, "exchange": exchange, "product": product},
        )
        return response if isinstance(response, dict) else {"status": "error"}

    def get_funds(self) -> Dict[str, Any]:
        response = self._client.funds()
        unwrapped = self._unwrap(response)
        if isinstance(unwrapped, dict):
            return {
                "available_margin": float(unwrapped.get("availablecash", 0.0)),
                **unwrapped,
            }
        return {}

    def get_margins(self, positions: List[Dict[str, Any]]) -> Dict[str, Any]:
        response = self._post("margins", {"positions": positions})
        return self._unwrap(response) or {}

    def cancel_all_orders(self) -> Dict[str, Any]:
        response = self._client.cancelallorder()
        return response if isinstance(response, dict) else {"status": "error"}

    # ------------------------------------------------------------------
    # Streaming feed helpers
    # ------------------------------------------------------------------
    def connect_feed(self) -> bool:
        connect = getattr(self._client, "connect", None)
        if not connect:
            return False
        connected = bool(connect())
        self._feed_connected = self._feed_connected or connected
        return connected

    def disconnect_feed(self) -> None:
        disconnect = getattr(self._client, "disconnect", None)
        if disconnect:
            disconnect()
        self._feed_connected = False

    def _ensure_feed(self) -> None:
        if not self._feed_connected:
            self.connect_feed()

    def subscribe_ltp(self, instruments: List[Dict[str, Any]], callback: Optional[Any] = None) -> bool:
        self._ensure_feed()
        return bool(self._client.subscribe_ltp(instruments, on_data_received=callback))

    def unsubscribe_ltp(self, instruments: List[Dict[str, Any]]) -> bool:
        return bool(self._client.unsubscribe_ltp(instruments))

    def subscribe_quote(self, instruments: List[Dict[str, Any]], callback: Optional[Any] = None) -> bool:
        self._ensure_feed()
        return bool(self._client.subscribe_quote(instruments, on_data_received=callback))

    def unsubscribe_quote(self, instruments: List[Dict[str, Any]]) -> bool:
        return bool(self._client.unsubscribe_quote(instruments))

    def subscribe_depth(self, instruments: List[Dict[str, Any]], callback: Optional[Any] = None) -> bool:
        self._ensure_feed()
        return bool(self._client.subscribe_depth(instruments, on_data_received=callback))

    def unsubscribe_depth(self, instruments: List[Dict[str, Any]]) -> bool:
        return bool(self._client.unsubscribe_depth(instruments))

    def get_ltp_snapshot(self, exchange: Optional[str] = None, symbol: Optional[str] = None) -> Dict[str, Any]:
        snapshot = self._client.get_ltp(exchange=exchange, symbol=symbol)
        return snapshot or {}

    def get_quote_snapshot(self, exchange: Optional[str] = None, symbol: Optional[str] = None) -> Dict[str, Any]:
        snapshot = self._client.get_quotes(exchange=exchange, symbol=symbol)
        return snapshot or {}

    def get_depth_snapshot(self, exchange: Optional[str] = None, symbol: Optional[str] = None) -> Dict[str, Any]:
        snapshot = self._client.get_depth(exchange=exchange, symbol=symbol)
        return snapshot or {}
