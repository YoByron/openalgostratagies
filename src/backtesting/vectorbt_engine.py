"""VectorBT based backtesting utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

try:
    import vectorbt as vbt
except ImportError as exc:  # noqa: N813
    raise ImportError("vectorbt must be installed to use VectorBTEngine") from exc


@dataclass(slots=True)
class BacktestResult:
    portfolio: Any
    stats: pd.Series


class VectorBTEngine:
    """Thin wrapper simplifying VectorBT usage for options strategy PnL."""

    def __init__(self, initial_capital: float = 100_000.0, fees: float = 0.0) -> None:
        self.initial_capital = initial_capital
        self.fees = fees

    def run_from_signals(
        self,
        prices: pd.Series,
        entries: pd.Series,
        exits: pd.Series,
        size: pd.Series | float | int = 1,
        direction: str = "long",
        custom_stats: Optional[Dict[str, Any]] = None,
    ) -> BacktestResult:
        pf = vbt.Portfolio.from_signals(
            close=prices,
            entries=entries,
            exits=exits,
            size=size,
            init_cash=self.initial_capital,
            fees=self.fees,
            direction=direction,
        )
        stats = pf.stats()
        if custom_stats:
            for key, func in custom_stats.items():
                stats.loc[key] = func(pf)
        return BacktestResult(portfolio=pf, stats=stats)

    def run_from_orders(
        self,
        prices: pd.Series,
        quantity: pd.Series,
        cash_sharing: bool = True,
    ) -> BacktestResult:
        pf = vbt.Portfolio.from_orders(
            close=prices,
            size=quantity,
            init_cash=self.initial_capital,
            fees=self.fees,
            cash_sharing=cash_sharing,
        )
        return BacktestResult(portfolio=pf, stats=pf.stats())

    @staticmethod
    def prepare_series(data: Any, index: Optional[pd.Index] = None) -> pd.Series:
        if isinstance(data, pd.Series):
            return data
        if isinstance(data, (list, tuple, np.ndarray)):
            return pd.Series(data, index=index)
        raise TypeError("Data must be a pandas Series, list, tuple, or numpy array")
