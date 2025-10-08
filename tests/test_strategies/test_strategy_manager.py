from datetime import datetime

from src.execution.order_manager import OrderRequest
from src.execution.position_tracker import PositionTracker
from src.risk.risk_controller import RiskDecision
from src.strategies.base_strategy import BaseStrategy, Signal, Position
from src.strategies.strategy_manager import StrategyManager


class DummyStrategy(BaseStrategy):
    def __init__(self) -> None:
        super().__init__(name="Dummy", params={})

    def generate_signal(self, market_data):
        return Signal(
            action="ENTER",
            legs=[{"action": "BUY", "quantity": 1, "option_type": "CE", "strike": 100}],
            reason="test",
            timestamp=datetime.now(),
        )

    def should_exit(self, position: Position, market_data):
        return False

    def calculate_position_size(self, available_capital: float) -> int:
        return 1


class DummyOrderManager:
    def __init__(self) -> None:
        self.submitted = []

    def submit_order(self, request: OrderRequest):
        self.submitted.append(request)


class DummyRiskController:
    def __init__(self):
        self.portfolio_value = 100_000
        self.last_exposures = None

    def update_portfolio_value(self, value):
        self.portfolio_value = value

    def update_returns(self, returns):
        pass

    def evaluate(self, exposures, positions, additional_margin, new_return=None):
        self.last_exposures = exposures
        return RiskDecision(True, [], 0.0, None)


class DummyMarketDataService:
    def snapshot(self, option_positions):
        from types import SimpleNamespace

        return SimpleNamespace(
            timestamp=datetime.utcnow(),
            spot_price=20000,
            portfolio_greeks={"delta": 10.0},
            option_chain=None,
        )


def test_strategy_manager_uses_market_data_service():
    order_manager = DummyOrderManager()
    tracker = PositionTracker()
    risk_controller = DummyRiskController()
    market_service = DummyMarketDataService()

    manager = StrategyManager(
        order_manager=order_manager,
        position_tracker=tracker,
        risk_controller=risk_controller,
        market_data_service=market_service,
        execution_mode="dry_run",
    )

    manager.register_strategy(DummyStrategy())
    manager.process_market_data({})

    assert risk_controller.last_exposures == {"delta": 10.0}


class BlockingRiskController(DummyRiskController):
    def evaluate(self, exposures, positions, additional_margin, new_return=None):  # type: ignore[override]
        return RiskDecision(False, ["blocked"], 0.0, None)


def test_strategy_manager_does_not_submit_when_risk_blocks():
    order_manager = DummyOrderManager()
    tracker = PositionTracker()
    risk_controller = BlockingRiskController()
    market_service = DummyMarketDataService()

    manager = StrategyManager(
        order_manager=order_manager,
        position_tracker=tracker,
        risk_controller=risk_controller,
        market_data_service=market_service,
        execution_mode="paper",
    )

    manager.register_strategy(DummyStrategy())
    manager.process_market_data({})

    assert order_manager.submitted == []
