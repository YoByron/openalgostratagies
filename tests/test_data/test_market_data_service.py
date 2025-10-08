from datetime import datetime

import pandas as pd

from src.data.market_data_service import MarketDataService


def test_market_data_snapshot(monkeypatch):
    service = MarketDataService(symbol="NIFTY", exchange="NFO")

    monkeypatch.setattr(
        "src.data.openalgo_client.openalgo.get_quotes",
        lambda symbol, exchange: {"ltp": 20050},
    )

    sample_chain = [
        {
            "strike": 20000,
            "call_delta": 0.3,
            "call_gamma": 0.01,
            "call_theta": -5,
            "call_vega": 10,
            "put_delta": -0.3,
            "put_gamma": 0.01,
            "put_theta": -5,
            "put_vega": 10,
            "call_oi": 1000,
            "call_oi_prev": 900,
            "put_oi": 1200,
            "put_oi_prev": 1100,
        }
    ]

    monkeypatch.setattr(
        "src.data.openalgo_client.openalgo.get_option_chain",
        lambda symbol, expiry: sample_chain,
    )

    option_positions = [
        {
            "option_type": "CE",
            "strike": 20000,
            "expiry": (datetime.utcnow().replace(microsecond=0)).isoformat(),
            "quantity": 1,
            "iv": 0.2,
        }
    ]

    snapshot = service.snapshot(option_positions)
    assert snapshot.spot_price == 20050
    assert isinstance(snapshot.option_chain, pd.DataFrame)
    assert "call_oi_change" in snapshot.option_chain.columns
    assert "delta" in snapshot.portfolio_greeks
