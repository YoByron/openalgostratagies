"""OTM strangle strategy implementation."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger

from config.strategy_config import STRATEGY_PARAMS
from src.data.options_chain import OptionsChainHandler
from src.strategies.base_strategy import BaseStrategy, Position, Signal


class StrangleStrategy(BaseStrategy):
    def __init__(self, symbol: str = "NIFTY") -> None:
        params = STRATEGY_PARAMS["strangle"]
        super().__init__(name="Strangle", params=params)
        self.symbol = symbol
        self.chain_handler = OptionsChainHandler(symbol)

        self.direction = params["direction"]
        self.call_delta = params["call_delta"]
        self.put_delta = params["put_delta"]
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
            logger.debug("Skipping short strangle due to low IV percentile", iv=iv_percentile)
            return None

        call_strikes = self.chain_handler.get_strikes_by_delta(self.call_delta, option_type="CE")
        put_strikes = self.chain_handler.get_strikes_by_delta(self.put_delta, option_type="PE")

        if not call_strikes or not put_strikes:
            logger.warning("Unable to determine strangle strikes", symbol=self.symbol)
            return None

        short_call = call_strikes[0]
        short_put = put_strikes[0]

        legs = self._build_legs(short_call, short_put)

        signal = Signal(
            action="ENTER",
            legs=legs,
            reason=f"Strangle {self.direction} entry",
            timestamp=datetime.now(),
            metadata={
                "call_strike": short_call,
                "put_strike": short_put,
                "dte": dte,
                "direction": self.direction,
            },
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
        risk_fraction = 0.05
        reference = 1200
        lots = int((available_capital * risk_fraction) / reference)
        return max(1, lots)

    def _build_legs(self, call_strike: float, put_strike: float) -> list[Dict[str, Any]]:
        action = "BUY" if self.direction == "long" else "SELL"
        hedge_action = "SELL" if action == "BUY" else "BUY"

        legs = [
            {"action": action, "strike": call_strike, "option_type": "CE", "quantity": 1},
            {"action": action, "strike": put_strike, "option_type": "PE", "quantity": 1},
        ]

        if self.direction == "short":
            width = 200
            legs.extend(
                [
                    {"action": hedge_action, "strike": call_strike + width, "option_type": "CE", "quantity": 1},
                    {"action": hedge_action, "strike": put_strike - width, "option_type": "PE", "quantity": 1},
                ]
            )
        return legs
