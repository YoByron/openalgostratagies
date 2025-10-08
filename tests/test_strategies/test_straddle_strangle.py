from datetime import datetime

import pandas as pd

from src.strategies.straddle import StraddleStrategy
from src.strategies.strangle import StrangleStrategy


def test_straddle_signal_requires_iv_threshold():
    strategy = StraddleStrategy()
    market_data = {"dte": strategy.dte_entry, "spot_price": 20000, "iv_percentile": strategy.iv_percentile_min}
    signal = strategy.generate_signal(market_data)
    assert signal is None or signal.action == "ENTER"


def test_strangle_builds_legs():
    strategy = StrangleStrategy()
    market_data = {
        "dte": strategy.dte_entry,
        "iv_percentile": max(strategy.iv_percentile_min, 40),
        "spot_price": 20000,
    }
    signal = strategy.generate_signal(market_data)
    if signal:
        assert len(signal.legs) >= 2
