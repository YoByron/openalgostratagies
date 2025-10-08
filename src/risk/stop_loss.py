"""Stop loss and take profit evaluation utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class StopLossConfig:
    stop_loss_pct: float
    take_profit_pct: float
    trailing_pct: Optional[float] = None


class StopLossManager:
    def __init__(self, config: StopLossConfig) -> None:
        self.config = config

    def evaluate(
        self,
        entry_price: float,
        current_price: float,
        direction: int = 1,
        extreme_price: Optional[float] = None,
    ) -> Optional[str]:
        if entry_price <= 0:
            raise ValueError("Entry price must be positive")

        pnl_pct = self._pnl_percentage(entry_price, current_price, direction)

        if pnl_pct <= -self.config.stop_loss_pct:
            return "stop_loss"
        if pnl_pct >= self.config.take_profit_pct:
            return "take_profit"

        if self.config.trailing_pct is not None and extreme_price is not None:
            if self._trailing_hit(entry_price, current_price, extreme_price, direction):
                return "trailing_stop"

        return None

    def _trailing_hit(
        self,
        entry_price: float,
        current_price: float,
        extreme_price: float,
        direction: int,
    ) -> bool:
        trailing_pct = self.config.trailing_pct or 0.0
        if direction > 0:
            if extreme_price <= entry_price:
                return False
            drop_pct = ((extreme_price - current_price) / extreme_price) * 100
            return drop_pct >= trailing_pct
        if extreme_price >= entry_price:
            return False
        rebound_pct = ((current_price - extreme_price) / extreme_price) * 100
        return rebound_pct >= trailing_pct

    @staticmethod
    def _pnl_percentage(entry_price: float, current_price: float, direction: int) -> float:
        change = (current_price - entry_price) / entry_price * 100
        return change if direction >= 0 else -change
