"""Delta neutral strategy implementation."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from config.strategy_config import STRATEGY_PARAMS
from src.strategies.base_strategy import BaseStrategy, Position, Signal


class DeltaNeutralStrategy(BaseStrategy):
    def __init__(self, symbol: str = "NIFTY") -> None:
        params = STRATEGY_PARAMS["delta_neutral"]
        super().__init__(name="DeltaNeutral", params=params)
        self.symbol = symbol

        self.delta_threshold = params["delta_threshold"]
        self.rebalance_frequency = params["rebalance_frequency"]
        self.target_allocation = params["target_allocation"]

    def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Signal]:
        current_delta = market_data.get("portfolio_delta", 0.0)
        timestamp = market_data.get("timestamp", datetime.now())

        if abs(current_delta) <= self.delta_threshold:
            return None

        adjustment = self._calculate_adjustment(current_delta)
        signal = Signal(
            action="ADJUST",
            legs=adjustment,
            reason=f"Rebalance to delta threshold {self.delta_threshold}",
            timestamp=timestamp,
            metadata={"current_delta": current_delta},
        )
        return signal

    def should_exit(self, position: Position, market_data: Dict[str, Any]) -> bool:
        return False

    def calculate_position_size(self, available_capital: float) -> int:
        return 1

    def _calculate_adjustment(self, current_delta: float) -> list[Dict[str, Any]]:
        direction = "SELL" if current_delta > 0 else "BUY"
        quantity = max(int(abs(current_delta) / 10), 1)
        legs = [
            {
                "action": direction,
                "symbol": self.symbol,
                "instrument": "FUT",
                "quantity": quantity,
            }
        ]
        return legs
