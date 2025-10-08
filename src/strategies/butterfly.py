"""Butterfly spread strategy implementation."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from config.strategy_config import STRATEGY_PARAMS
from src.data.options_chain import OptionsChainHandler
from src.strategies.base_strategy import BaseStrategy, Position, Signal


class ButterflyStrategy(BaseStrategy):
    def __init__(self, symbol: str = "NIFTY") -> None:
        params = STRATEGY_PARAMS["butterfly"]
        super().__init__(name="Butterfly", params=params)
        self.symbol = symbol
        self.chain_handler = OptionsChainHandler(symbol)

        self.wing_width = params["wing_width"]
        self.atm_offset = params["atm_offset"]
        self.dte_entry = params["dte_entry"]
        self.dte_exit = params["dte_exit"]
        self.profit_target = params["profit_target"]
        self.stop_loss = params["stop_loss"]

    def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Signal]:
        if self.positions:
            return None

        dte = market_data.get("dte", self.dte_entry)
        if dte != self.dte_entry:
            return None

        spot = market_data.get("spot_price")
        center_strike = self.chain_handler.get_atm_strike(spot) + self.atm_offset

        legs = [
            {"action": "SELL", "strike": center_strike, "option_type": "CE", "quantity": 2},
            {"action": "BUY", "strike": center_strike + self.wing_width, "option_type": "CE", "quantity": 1},
            {"action": "BUY", "strike": center_strike - self.wing_width, "option_type": "CE", "quantity": 1},
        ]

        signal = Signal(
            action="ENTER",
            legs=legs,
            reason="Enter call butterfly",
            timestamp=datetime.now(),
            metadata={"center": center_strike, "dte": dte},
        )
        return signal

    def should_exit(self, position: Position, market_data: Dict[str, Any]) -> bool:
        dte = market_data.get("dte", self.dte_entry)
        if dte <= self.dte_exit:
            return True

        pnl = position.pnl
        reference = abs(position.entry_price)

        if pnl >= reference * self.profit_target:
            return True
        if pnl <= -reference * self.stop_loss:
            return True
        return False

    def calculate_position_size(self, available_capital: float) -> int:
        risk_fraction = 0.04
        reference = self.wing_width * 50
        lots = int((available_capital * risk_fraction) / max(reference, 1))
        return max(1, lots)
