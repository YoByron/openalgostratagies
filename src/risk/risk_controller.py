"""Coordinate VaR, margin, and risk limit checks."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterable, Mapping, Optional

import pandas as pd

from config.settings import settings
from src.risk.margin_monitor import MarginCheckResult, MarginMonitor
from src.risk.risk_limits import RiskLimitsChecker
from src.risk.var_calculator import VaRCalculator, VaRConfig


@dataclass(slots=True)
class RiskDecision:
    approved: bool
    reasons: list[str]
    var: float
    margin: Optional[MarginCheckResult] = None


class RiskController:
    def __init__(
        self,
        portfolio_value: float,
        var_calculator: Optional[VaRCalculator] = None,
        margin_monitor: Optional[MarginMonitor] = None,
        risk_limits: Optional[RiskLimitsChecker] = None,
    ) -> None:
        self.portfolio_value = portfolio_value
        self.var_calculator = var_calculator or VaRCalculator(VaRConfig())
        self.margin_monitor = margin_monitor or MarginMonitor()
        self.risk_limits = risk_limits or RiskLimitsChecker.from_settings()
        self._returns: deque[float] = deque(maxlen=500)

    def update_returns(self, returns: Iterable[float] | float) -> None:
        if isinstance(returns, (int, float)):
            self._returns.append(float(returns))
            return
        for value in returns:
            self._returns.append(float(value))

    def update_portfolio_value(self, value: float) -> None:
        self.portfolio_value = value

    def current_var(self) -> float:
        if not self._returns:
            return 0.0
        series = pd.Series(self._returns)
        return float(self.var_calculator.calculate(series, self.portfolio_value))

    def evaluate(
        self,
        exposures: Optional[Mapping[str, float]],
        positions: Optional[Iterable[Mapping[str, object]]] = None,
        additional_margin: float = 0.0,
        new_return: Optional[float] = None,
    ) -> RiskDecision:
        if new_return is not None:
            self.update_returns(new_return)

        exposures = exposures or {}
        var_value = self.current_var()
        reasons: list[str] = []

        limits_ok = self.risk_limits.greeks_within_limits(exposures)
        if not limits_ok:
            reasons.append("greeks_limits_exceeded")

        var_limit = settings.MAX_LOSS_PER_TRADE
        var_ok = var_limit <= 0 or var_value <= var_limit
        if not var_ok:
            reasons.append("var_limit_exceeded")

        margin_result: Optional[MarginCheckResult] = None
        margin_ok = True
        if positions is not None:
            margin_result = self.margin_monitor.check_positions(positions)
            margin_ok = margin_result.is_within_limit
        if margin_ok:
            margin_ok = self.margin_monitor.has_sufficient_margin(additional_margin)
        if not margin_ok:
            reasons.append("margin_limit_exceeded")

        approved = not reasons
        return RiskDecision(approved=approved, reasons=reasons, var=var_value, margin=margin_result)
