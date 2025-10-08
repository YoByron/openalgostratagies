import pandas as pd

from src.risk.margin_monitor import MarginMonitor
from src.risk.var_calculator import VaRCalculator, VaRConfig


def test_var_historical_non_negative():
    returns = pd.Series([0.01, -0.02, 0.015, -0.005])
    calc = VaRCalculator(VaRConfig(confidence_level=0.95, method="historical"))
    var = calc.calculate(returns, portfolio_value=1_000_000)
    assert var >= 0


def test_margin_monitor_has_limit():
    monitor = MarginMonitor(
        max_utilization_pct=0.5,
        margin_fetcher=lambda positions: {"span_margin": 10000},
        funds_fetcher=lambda: {"available_margin": 50000},
    )
    result = monitor.check_positions([{"symbol": "NIFTY", "quantity": 1}])
    assert result.is_within_limit
