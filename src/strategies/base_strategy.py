"""Base interfaces shared by all strategy implementations."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger


@dataclass
class Position:
    """Represents a single option leg within a strategy."""

    symbol: str
    strike: float
    option_type: str
    quantity: int
    entry_price: float
    current_price: float
    expiry: str
    order_id: Optional[str] = None

    @property
    def pnl(self) -> float:
        """Return mark-to-market profit/loss for the leg."""

        return (self.current_price - self.entry_price) * self.quantity

    @property
    def pnl_pct(self) -> float:
        """Return percentage profit/loss for the leg."""

        if self.entry_price == 0:
            return 0.0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100


@dataclass
class Signal:
    """Represents the intent to enter/exit/adjust a strategy position."""

    action: str
    legs: List[Dict[str, Any]]
    reason: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class BaseStrategy(ABC):
    """Common behaviour across options strategies."""

    def __init__(self, name: str, params: Dict[str, Any]) -> None:
        self.name = name
        self.params = params
        self.positions: List[Position] = []
        self.signals: List[Signal] = []

    @abstractmethod
    def generate_signal(self, market_data: Dict[str, Any]) -> Optional[Signal]:
        """Generate an entry signal if conditions are satisfied."""

    @abstractmethod
    def should_exit(self, position: Position, market_data: Dict[str, Any]) -> bool:
        """Return whether the provided position should be closed."""

    @abstractmethod
    def calculate_position_size(self, available_capital: float) -> int:
        """Determine the number of lots/contracts to trade."""

    def update_positions(self, current_prices: Dict[str, float]) -> None:
        """Refresh mark-to-market prices on held positions."""

        for position in self.positions:
            key = f"{position.symbol}_{position.strike}_{position.option_type}"
            if key in current_prices:
                position.current_price = current_prices[key]

    def get_total_pnl(self) -> float:
        """Return aggregate P&L across all open positions."""

        return sum(position.pnl for position in self.positions)

    def get_portfolio_greeks(self) -> Dict[str, float]:
        """Placeholder for portfolio level greeks aggregation."""

        return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}

    def add_position(self, position: Position) -> None:
        """Track a newly opened leg."""

        self.positions.append(position)
        logger.info(
            "Position added",
            symbol=position.symbol,
            strike=position.strike,
            option_type=position.option_type,
        )

    def remove_position(self, position: Position) -> None:
        """Stop tracking a closed leg."""

        if position in self.positions:
            self.positions.remove(position)
            logger.info(
                "Position removed",
                symbol=position.symbol,
                strike=position.strike,
                option_type=position.option_type,
            )

    def log_signal(self, signal: Signal) -> None:
        """Persist the generated signal for audit/tracking."""

        self.signals.append(signal)
        logger.info("Signal generated", action=signal.action, reason=signal.reason)

    def get_strategy_state(self) -> Dict[str, Any]:
        """Return current bookkeeping snapshot for the strategy."""

        return {
            "name": self.name,
            "positions": len(self.positions),
            "total_pnl": self.get_total_pnl(),
            "signals": len(self.signals),
        }
