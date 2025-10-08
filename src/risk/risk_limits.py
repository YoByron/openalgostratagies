"""Risk guardrails for strategies and portfolios."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from config.settings import settings


@dataclass(slots=True)
class RiskThresholds:
    max_delta: float
    max_gamma: float
    max_vega: float
    max_position_pct: float
    max_drawdown_pct: float
    max_loss_per_trade: float


class RiskLimitsChecker:
    """Applies configured limits to positions and portfolio exposures."""

    def __init__(self, thresholds: RiskThresholds) -> None:
        self.thresholds = thresholds

    @classmethod
    def from_settings(cls) -> "RiskLimitsChecker":
        thresholds = RiskThresholds(
            max_delta=settings.MAX_PORTFOLIO_DELTA,
            max_gamma=settings.MAX_PORTFOLIO_GAMMA,
            max_vega=settings.MAX_PORTFOLIO_VEGA,
            max_position_pct=settings.MAX_POSITION_SIZE_PCT,
            max_drawdown_pct=settings.MAX_DRAWDOWN_PCT,
            max_loss_per_trade=settings.MAX_LOSS_PER_TRADE,
        )
        return cls(thresholds)

    def greeks_within_limits(self, exposures: Mapping[str, float]) -> bool:
        return (
            abs(exposures.get("delta", 0.0)) <= self.thresholds.max_delta
            and abs(exposures.get("gamma", 0.0)) <= self.thresholds.max_gamma
            and abs(exposures.get("vega", 0.0)) <= self.thresholds.max_vega
        )

    def position_within_limit(self, notional_pct: float) -> bool:
        return notional_pct <= self.thresholds.max_position_pct

    def trade_loss_within_limit(self, loss_amount: float) -> bool:
        return abs(loss_amount) <= self.thresholds.max_loss_per_trade

    def drawdown_within_limit(self, drawdown_pct: float) -> bool:
        return drawdown_pct <= self.thresholds.max_drawdown_pct
