from dataclasses import dataclass

import pandas as pd

from src.risk.margin_monitor import MarginCheckResult
from src.risk.risk_controller import RiskController, RiskDecision
from src.risk.risk_limits import RiskLimitsChecker, RiskThresholds
from src.risk.var_calculator import VaRCalculator, VaRConfig


class StubVaRCalculator(VaRCalculator):
    def __init__(self, value: float) -> None:
        self.value = value

    def calculate(self, returns: pd.Series, portfolio_value: float) -> float:  # type: ignore[override]
        return self.value


class StubMarginMonitor:
    def __init__(self, within_limit: bool, sufficient_additional: bool = True) -> None:
        self.within_limit = within_limit
        self.sufficient_additional = sufficient_additional
        self.checked_positions = None

    def check_positions(self, positions):
        self.checked_positions = list(positions)
        return MarginCheckResult(
            required_margin=10_000,
            available_margin=20_000,
            deficit=0.0 if self.within_limit else 5_000,
            is_within_limit=self.within_limit,
        )

    def has_sufficient_margin(self, additional_requirement: float) -> bool:
        return self.sufficient_additional


class StubRiskLimits(RiskLimitsChecker):
    def __init__(self, greeks_ok: bool) -> None:
        thresholds = RiskThresholds(100, 50, 500, 0.05, 10, 2000)
        super().__init__(thresholds)
        self.greeks_ok = greeks_ok

    def greeks_within_limits(self, exposures):  # type: ignore[override]
        return self.greeks_ok


def make_controller(var_value: float, greeks_ok: bool, margin_within: bool, margin_additional_ok: bool) -> RiskController:
    controller = RiskController(
        portfolio_value=100_000,
        var_calculator=StubVaRCalculator(var_value),
        margin_monitor=StubMarginMonitor(margin_within, margin_additional_ok),
        risk_limits=StubRiskLimits(greeks_ok),
    )
    controller.update_returns([0.01, -0.005])
    return controller


def test_risk_controller_approves_when_all_checks_pass():
    controller = make_controller(var_value=100, greeks_ok=True, margin_within=True, margin_additional_ok=True)
    decision = controller.evaluate(exposures={"delta": 10}, positions=[{"symbol": "NIFTY", "quantity": 1}])
    assert decision.approved
    assert decision.reasons == []


def test_risk_controller_blocks_on_greeks_and_margin():
    controller = make_controller(var_value=100, greeks_ok=False, margin_within=False, margin_additional_ok=False)
    decision = controller.evaluate(exposures={"delta": 999}, positions=[{"symbol": "NIFTY", "quantity": 1}])
    assert not decision.approved
    assert "greeks_limits_exceeded" in decision.reasons
    assert "margin_limit_exceeded" in decision.reasons


def test_risk_controller_blocks_on_var_limit():
    controller = make_controller(var_value=10_000, greeks_ok=True, margin_within=True, margin_additional_ok=True)
    decision = controller.evaluate(exposures={}, positions=None)
    assert not decision.approved
    assert "var_limit_exceeded" in decision.reasons
