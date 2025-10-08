"""Iron Condor strategy implementation."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from config.strategy_config import STRATEGY_PARAMS
from src.data.options_chain import OptionsChainHandler
from src.strategies.base_strategy import BaseStrategy, Position, Signal


class IronCondorStrategy(BaseStrategy):
    """Delta-targeted iron condor strategy for Indian index options."""

    def __init__(self, symbol: str = "NIFTY") -> None:
        params = STRATEGY_PARAMS["iron_condor"]
        super().__init__(name="IronCondor", params=params)

        self.symbol = symbol
        self.chain_handler = OptionsChainHandler(symbol)

        self.call_width = params["call_width"]
        self.put_width = params["put_width"]
        self.target_delta = params["target_delta"]
        self.dte_entry = params["dte_entry"]
        self.dte_exit = params["dte_exit"]
        self.profit_target = params["profit_target"]
        self.stop_loss = params["stop_loss"]
        self.max_positions = params["max_positions"]

    def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Signal]:
        """Return an entry signal when condor conditions are met."""

        if len(self.positions) >= self.max_positions:
            return None

        dte = market_data.get("dte", self.dte_entry)
        if dte != self.dte_entry:
            return None

        spot_price = market_data.get("spot_price")
        atm_strike = self.chain_handler.get_atm_strike(spot_price)

        call_strikes = self.chain_handler.get_strikes_by_delta(
            self.target_delta,
            option_type="CE",
        )
        put_strikes = self.chain_handler.get_strikes_by_delta(
            self.target_delta,
            option_type="PE",
        )

        if not call_strikes or not put_strikes:
            logger.warning("Unable to identify condor strikes", symbol=self.symbol)
            return None

        short_call = call_strikes[0]
        long_call = short_call + self.call_width
        short_put = put_strikes[0]
        long_put = short_put - self.put_width

        legs = [
            {"action": "SELL", "strike": short_call, "option_type": "CE", "quantity": 1},
            {"action": "BUY", "strike": long_call, "option_type": "CE", "quantity": 1},
            {"action": "SELL", "strike": short_put, "option_type": "PE", "quantity": 1},
            {"action": "BUY", "strike": long_put, "option_type": "PE", "quantity": 1},
        ]

        signal = Signal(
            action="ENTER",
            legs=legs,
            reason=f"Entry DTE={dte} ATM={atm_strike}",
            timestamp=datetime.now(),
            metadata={
                "atm_strike": atm_strike,
                "dte": dte,
                "max_profit": self._calculate_max_profit(legs, market_data),
                "max_loss": self._calculate_max_loss(legs),
            },
        )
        return signal

    def should_exit(self, position: Position, market_data: Dict[str, Any]) -> bool:
        """Check stop/profit/DTE exit conditions."""

        dte = market_data.get("dte", self.dte_entry)
        if dte <= self.dte_exit:
            logger.info("Exiting condor due to DTE threshold", dte=dte)
            return True

        pnl = position.pnl
        max_profit = position.entry_price
        if pnl >= max_profit * self.profit_target:
            logger.info("Condor profit target reached", pnl=pnl)
            return True

        max_loss = max_profit * self.stop_loss
        if abs(pnl) >= max_loss:
            logger.info("Condor stop loss hit", pnl=pnl)
            return True

        return False

    def calculate_position_size(self, available_capital: float) -> int:
        """Risk ~5% of available capital per iron condor structure."""

        risk_cap = available_capital * 0.05
        max_loss = max(self.call_width, self.put_width)
        lots = int(risk_cap / max_loss)
        return max(1, lots)

    def _calculate_max_profit(self, legs: List[Dict[str, Any]], market_data: Dict[str, Any]) -> float:
        """Placeholder for max profit (requires pricing data)."""

        _ = legs, market_data
        return 0.0

    def _calculate_max_loss(self, legs: List[Dict[str, Any]]) -> float:
        """Max loss approximated by the wider spread width."""

        _ = legs
        return float(max(self.call_width, self.put_width))

    def adjust_position(self, position: Position, market_data: Dict[str, Any]) -> Optional[Signal]:
        """Placeholder for future adjustment rules."""

        _ = position, market_data
        return None
