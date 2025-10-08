from datetime import datetime

from src.execution.order_manager import OrderRequest
from src.execution.position_tracker import PositionTracker
from src.risk.margin_monitor import MarginMonitor
from src.risk.risk_controller import RiskController
from src.strategies.iron_condor import IronCondorStrategy
from src.strategies.strategy_manager import StrategyManager


class RecordingOrderManager:
    def __init__(self) -> None:
        self.orders = []

    def submit_order(self, request: OrderRequest):
        self.orders.append(request)


def test_strategy_flow_with_mocked_market_data(monkeypatch):
    order_manager = RecordingOrderManager()
    position_tracker = PositionTracker()

    margin_monitor = MarginMonitor(
        max_utilization_pct=0.8,
        margin_fetcher=lambda positions: {"span_margin": 5_000},
        funds_fetcher=lambda: {"available_margin": 100_000},
    )

    risk_controller = RiskController(
        portfolio_value=200_000,
        margin_monitor=margin_monitor,
    )

    strategy = IronCondorStrategy("NIFTY")

    manager = StrategyManager(
        order_manager=order_manager,
        position_tracker=position_tracker,
        risk_controller=risk_controller,
        execution_mode="paper",
    )

    manager.register_strategy(strategy)

    monkeypatch.setattr(
        "src.strategies.iron_condor.OptionsChainHandler.get_strikes_by_delta",
        lambda self, target_delta, option_type="CE", expiry=None: [20000],
    )

    market_context = {
        "portfolio_value": 200_000,
        "returns": 0.001,
        "portfolio_greeks": {"delta": 500.0, "gamma": 5.0, "vega": 100.0},
        "estimated_margin": 3_000,
        "spot_price": 20050,
        "dte": strategy.dte_entry,
    }

    manager.process_market_data(market_context)

    assert order_manager.orders == []
