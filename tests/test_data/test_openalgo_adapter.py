import types

import pytest

from src.data.openalgo_adapter import OpenAlgoSDKAdapter


class DummyAPI:
    def __init__(self, api_key: str, host: str) -> None:  # noqa: D401 - simple stub
        self.api_key = api_key
        self.host = host
        self.headers = {"Content-Type": "application/json"}
        self.place_calls = []
        self.connected = False
        self.ltp_subscriptions = []
        self.quote_subscriptions = []
        self.depth_subscriptions = []
        self.ltp_callback = None
        self.quote_callback = None
        self.depth_callback = None

    def quotes(self, *, symbol: str, exchange: str):  # noqa: D401 - simple stub
        return {"status": "success", "data": {"symbol": symbol, "exchange": exchange, "ltp": 123.45}}

    def depth(self, *, symbol: str, exchange: str):  # noqa: D401 - simple stub
        return {"status": "success", "data": {"bids": [], "asks": []}}

    def connect(self):  # noqa: D401 - simple stub
        self.connected = True
        return True

    def disconnect(self) -> None:  # noqa: D401 - simple stub
        self.connected = False

    def placeorder(self, **payload):  # noqa: D401 - simple stub
        self.place_calls.append(payload)
        return {"orderid": "abc123", "status": "success"}

    def cancelorder(self, *, order_id: str):  # noqa: D401 - simple stub
        return {"orderid": order_id, "status": "success"}

    def orderbook(self):  # noqa: D401 - simple stub
        return {"status": "success", "data": {"orders": [{"orderid": "abc123"}]}}

    def positionbook(self):  # noqa: D401 - simple stub
        return {"status": "success", "data": [{"symbol": "NIFTY", "quantity": "1"}]}

    def holdings(self):  # noqa: D401 - simple stub
        return {"status": "success", "data": {"holdings": [{"symbol": "NIFTY", "quantity": 1}]}}

    def funds(self):  # noqa: D401 - simple stub
        return {
            "status": "success",
            "data": {
                "availablecash": "1000.50",
                "collateral": "0.00",
            },
        }

    def cancelallorder(self):  # noqa: D401 - simple stub
        return {"status": "success"}

    def subscribe_ltp(self, instruments, on_data_received=None):  # noqa: D401 - simple stub
        self.ltp_subscriptions = instruments
        self.ltp_callback = on_data_received
        if self.ltp_callback:
            self.ltp_callback({"type": "market_data", "data": {"ltp": 125.0}})
        return True

    def unsubscribe_ltp(self, instruments):  # noqa: D401 - simple stub
        self.ltp_subscriptions = []
        return True

    def subscribe_quote(self, instruments, on_data_received=None):  # noqa: D401 - simple stub
        self.quote_subscriptions = instruments
        self.quote_callback = on_data_received
        return True

    def unsubscribe_quote(self, instruments):  # noqa: D401 - simple stub
        self.quote_subscriptions = []
        return True

    def subscribe_depth(self, instruments, on_data_received=None):  # noqa: D401 - simple stub
        self.depth_subscriptions = instruments
        self.depth_callback = on_data_received
        return True

    def unsubscribe_depth(self, instruments):  # noqa: D401 - simple stub
        self.depth_subscriptions = []
        return True

    def get_ltp(self, exchange=None, symbol=None):  # noqa: D401 - simple stub
        return {"ltp": 125.0, "exchange": exchange or "NFO", "symbol": symbol or "NIFTY"}

    def get_quotes(self, exchange=None, symbol=None):  # noqa: D401 - simple stub
        return {"quote": {"ltp": 124.0}, "exchange": exchange, "symbol": symbol}

    def get_depth(self, exchange=None, symbol=None):  # noqa: D401 - simple stub
        return {"depth": {"buy": [], "sell": []}, "exchange": exchange, "symbol": symbol}


@pytest.fixture
def adapter(monkeypatch):
    monkeypatch.setattr("src.data.openalgo_adapter.OpenAlgoAPI", DummyAPI)
    instance = OpenAlgoSDKAdapter(api_key="test", host="http://localhost:5000")

    def fake_post(endpoint: str, payload):
        if endpoint == "optionchain":
            return {"data": [{"strike": 20000, "call_delta": 0.3}]}
        if endpoint == "margins":
            return {"data": {"span_margin": 1500.0}}
        raise AssertionError(f"Unexpected endpoint {endpoint}")

    instance._post = types.MethodType(lambda self, ep, payload: fake_post(ep, payload), instance)
    return instance


def test_adapter_normalizes_quotes_and_orders(adapter):
    quotes = adapter.get_quotes("NIFTY", "NFO")
    assert quotes["ltp"] == 123.45

    order_response = adapter.place_order(
        symbol="NIFTY",
        exchange="NFO",
        action="BUY",
        quantity=1,
        price=100.0,
        product="MIS",
        order_type="LIMIT",
    )
    assert order_response["order_id"] == "abc123"

    cancel_response = adapter.cancel_order("abc123")
    assert cancel_response["order_id"] == "abc123"


def test_adapter_unwraps_structured_payloads(adapter):
    chain = adapter.get_option_chain("NIFTY", "2024-01-01")
    assert chain[0]["strike"] == 20000

    positions = adapter.get_positions()
    assert positions[0]["symbol"] == "NIFTY"

    holdings = adapter.get_holdings()
    assert holdings[0]["symbol"] == "NIFTY"

    funds = adapter.get_funds()
    assert funds["available_margin"] == pytest.approx(1000.50)

    margins = adapter.get_margins([{"symbol": "NIFTY"}])
    assert margins["span_margin"] == 1500.0


def test_adapter_order_book_and_cancel_all(adapter):
    order_book = adapter.get_order_book()
    assert order_book[0]["orderid"] == "abc123"

    response = adapter.cancel_all_orders()
    assert response["status"] == "success"


def test_adapter_feed_subscription_flow(adapter):
    dummy_client = adapter._client  # type: ignore[attr-defined]
    events = []
    instruments = [{"exchange": "NFO", "symbol": "NIFTY"}]

    subscribed = adapter.subscribe_ltp(instruments, callback=lambda data: events.append(data))
    assert subscribed is True
    assert dummy_client.connected is True
    assert dummy_client.ltp_subscriptions == instruments
    assert events  # callback invoked

    quote_subscribed = adapter.subscribe_quote(instruments)
    depth_subscribed = adapter.subscribe_depth(instruments)
    assert quote_subscribed and depth_subscribed

    ltp_snapshot = adapter.get_ltp_snapshot()
    assert ltp_snapshot["ltp"] == 125.0

    quote_snapshot = adapter.get_quote_snapshot()
    assert "quote" in quote_snapshot

    depth_snapshot = adapter.get_depth_snapshot()
    assert "depth" in depth_snapshot

    assert adapter.unsubscribe_ltp(instruments) is True
    assert adapter.unsubscribe_quote(instruments) is True
    assert adapter.unsubscribe_depth(instruments) is True

    adapter.disconnect_feed()
    assert dummy_client.connected is False
