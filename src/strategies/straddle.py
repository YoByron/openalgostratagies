"""ATM straddle strategy implementation."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger

from config.strategy_config import STRATEGY_PARAMS
from src.data.options_chain import OptionsChainHandler
from src.strategies.base_strategy import BaseStrategy, Position, Signal


class StraddleStrategy(BaseStrategy):
    def __init__(self, symbol: str = "NIFTY") -> None:
        params = STRATEGY_PARAMS["straddle"]
        super().__init__(name="Straddle", params=params)
        self.symbol = symbol
        self.chain_handler = OptionsChainHandler(symbol)

        self.direction = params["direction"]
        self.atm_offset = params["atm_offset"]
        self.dte_entry = params["dte_entry"]
        self.dte_exit = params["dte_exit"]
        self.profit_target = params["profit_target"]
        self.stop_loss = params["stop_loss"]
        self.iv_percentile_min = params["iv_percentile_min"]

    def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Signal]:
        if self.positions:
            return None

        dte = market_data.get("dte", self.dte_entry)
        if dte != self.dte_entry:
            return None

        iv_percentile = market_data.get("iv_percentile", 50)
        if iv_percentile < self.iv_percentile_min and self.direction == "short":
            logger.debug("Skipping short straddle due to low IV percentile", iv=iv_percentile)
            return None

        spot = market_data.get("spot_price")
        atm = self.chain_handler.get_atm_strike(spot) + self.atm_offset

        legs = self._build_legs(atm)
        if not legs:
            return None

        signal = Signal(
            action="ENTER",
            legs=legs,
            reason=f"Straddle {self.direction} entry at strike {atm}",
            timestamp=datetime.now(),
            metadata={"strike": atm, "dte": dte, "direction": self.direction},
        )
        return signal

    def should_exit(self, position: Position, market_data: Dict[str, Any]) -> bool:
        dte = market_data.get("dte", self.dte_entry)
        if dte <= self.dte_exit:
            return True

        pnl = position.pnl
        max_profit_reference = abs(position.entry_price)

        if self.direction == "long":
            if pnl >= max_profit_reference * self.profit_target:
                return True
            if pnl <= -max_profit_reference * self.stop_loss:
                return True
        else:
            if pnl >= max_profit_reference * self.profit_target:
                return True
            if pnl <= -max_profit_reference * self.stop_loss:
                return True
        return False

    def calculate_position_size(self, available_capital: float) -> int:
        risk_fraction = 0.05
        reference = 1000  # placeholder risk per straddle
        lots = int((available_capital * risk_fraction) / reference)
        return max(1, lots)

    def _build_legs(self, strike: float) -> Optional[list[Dict[str, Any]]]:
        action = "BUY" if self.direction == "long" else "SELL"
        hedge_action = "SELL" if action == "BUY" else "BUY"

        legs = [
            {"action": action, "strike": strike, "option_type": "CE", "quantity": 1},
            {"action": action, "strike": strike, "option_type": "PE", "quantity": 1},
        ]

        if self.direction == "short":
            legs.extend(
                [
                    {"action": hedge_action, "strike": strike + 200, "option_type": "CE", "quantity": 1},
                    {"action": hedge_action, "strike": strike - 200, "option_type": "PE", "quantity": 1},
                ]
            )
        return legs
