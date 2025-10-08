"""Position sizing helpers for options portfolios."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PositionSizingConfig:
    capital: float
    max_position_pct: float = 0.05
    max_portfolio_risk_pct: float = 0.02


class PositionSizer:
    """Provides different sizing models for strategy legs."""

    def __init__(self, config: PositionSizingConfig) -> None:
        self.config = config

    def fixed_fractional(self, stop_loss_per_unit: float, contract_multiplier: int = 1) -> int:
        risk_cap = self.config.capital * self.config.max_portfolio_risk_pct
        if stop_loss_per_unit <= 0:
            raise ValueError("Stop loss per unit must be positive")
        units = int(risk_cap / (stop_loss_per_unit * contract_multiplier))
        return max(units, 0)

    def notional_cap(self, contract_price: float, contract_multiplier: int = 1) -> int:
        notional_cap = self.config.capital * self.config.max_position_pct
        if contract_price <= 0:
            raise ValueError("Contract price must be positive")
        units = int(notional_cap / (contract_price * contract_multiplier))
        return max(units, 0)

    @staticmethod
    def kelly_fraction(win_probability: float, win_loss_ratio: float) -> float:
        if not 0 < win_probability < 1:
            raise ValueError("Win probability must be between 0 and 1")
        if win_loss_ratio <= 0:
            raise ValueError("Win/loss ratio must be positive")
        edge = (win_probability * (win_loss_ratio + 1)) - 1
        return max(edge / win_loss_ratio, 0.0)

    def kelly_position(self, win_probability: float, win_loss_ratio: float, contract_price: float, contract_multiplier: int = 1) -> int:
        fraction = self.kelly_fraction(win_probability, win_loss_ratio)
        notional = self.config.capital * min(fraction, self.config.max_position_pct)
        if contract_price <= 0:
            raise ValueError("Contract price must be positive")
        units = int(notional / (contract_price * contract_multiplier))
        return max(units, 0)

    @staticmethod
    def margin_capped(margin_per_lot: float, available_margin: float) -> int:
        if margin_per_lot <= 0:
            raise ValueError("Margin per lot must be positive")
        units = int(available_margin / margin_per_lot)
        return max(units, 0)
