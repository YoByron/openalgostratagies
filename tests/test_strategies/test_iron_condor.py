from datetime import datetime

import pandas as pd

from src.strategies.base_strategy import Position
from src.strategies.iron_condor import IronCondorStrategy


def test_generate_signal_requires_dte_entry():
    strategy = IronCondorStrategy()
    market_data = {"dte": strategy.dte_entry, "spot_price": 20000, "options_chain": pd.DataFrame()}
    signal = strategy.generate_signal(market_data)
    assert signal is None or signal.action == "ENTER"


def test_should_exit_on_dte_threshold():
    strategy = IronCondorStrategy()
    position = Position(
        symbol="NIFTY",
        strike=20000,
        option_type="CE",
        quantity=1,
        entry_price=100,
        current_price=80,
        expiry="2024-01-01",
    )
    market_data = {"dte": strategy.dte_exit}
    assert strategy.should_exit(position, market_data)
