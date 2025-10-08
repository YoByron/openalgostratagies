"""Calendar spread strategy implementation."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from config.strategy_config import STRATEGY_PARAMS
from src.data.options_chain import OptionsChainHandler
from src.strategies.base_strategy import BaseStrategy, Position, Signal


class CalendarSpreadStrategy(BaseStrategy):
    def __init__(self, symbol: str = "NIFTY") -> None:
        params = STRATEGY_PARAMS["calendar_spread"]
        super().__init__(name="CalendarSpread", params=params)
        self.symbol = symbol
        self.chain_handler = OptionsChainHandler(symbol)

        self.strike_selection = params["strike_selection"]
        self.front_month_dte = params["front_month_dte"]
        self.back_month_dte = params["back_month_dte"]
        self.profit_target = params["profit_target"]
        self.stop_loss = params["stop_loss"]

    def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Signal]:
        if self.positions:
            return None

        expiries = self.chain_handler.get_expiry_dates(num_expiries=4)
        if len(expiries) < 2:
            return None

        front_expiry = expiries[0]
        back_expiry = expiries[1]

        spot = market_data.get("spot_price")
        strike = self._select_strike(spot)

        legs = [
            {"action": "SELL", "strike": strike, "option_type": "CE", "quantity": 1, "expiry": front_expiry},
            {"action": "BUY", "strike": strike, "option_type": "CE", "quantity": 1, "expiry": back_expiry},
        ]

        signal = Signal(
            action="ENTER",
            legs=legs,
            reason="Long call calendar spread",
            timestamp=datetime.now(),
            metadata={"front_expiry": front_expiry, "back_expiry": back_expiry, "strike": strike},
        )
        return signal

    def should_exit(self, position: Position, market_data: Dict[str, Any]) -> bool:
        pnl = position.pnl
        reference = abs(position.entry_price)

        if pnl >= reference * self.profit_target:
            return True
        if pnl <= -reference * self.stop_loss:
            return True
        return False

    def calculate_position_size(self, available_capital: float) -> int:
        risk_fraction = 0.05
        reference = 800
        lots = int((available_capital * risk_fraction) / reference)
        return max(1, lots)

    def _select_strike(self, spot: Optional[float]) -> float:
        atm = self.chain_handler.get_atm_strike(spot)
        if self.strike_selection == "otm":
            return atm + 100
        if self.strike_selection == "itm":
            return atm - 100
        return atm
