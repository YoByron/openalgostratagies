"""Helpers for working with options chain data."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
from loguru import logger

from config.strategy_config import CONTRACT_SPECS
from src.data.openalgo_client import openalgo


class OptionsChainHandler:
    """Utility to fetch and transform option chain information."""

    def __init__(self, symbol: str = "NIFTY") -> None:
        self.symbol = symbol
        self.contract_spec = CONTRACT_SPECS.get(symbol, {})

    def get_expiry_dates(self, num_expiries: int = 4) -> List[str]:
        """Return the next ``num_expiries`` expiry dates as ISO strings."""

        today = datetime.now()
        expiries = [
            (today + timedelta(weeks=index)).strftime("%Y-%m-%d")
            for index in range(num_expiries)
        ]
        return expiries

    def get_chain(self, expiry: Optional[str] = None) -> pd.DataFrame:
        """Fetch the option chain for the provided expiry."""

        target_expiry = expiry or self.get_expiry_dates()[0]
        try:
            chain_data = openalgo.get_option_chain(self.symbol, target_expiry)
            frame = pd.DataFrame(chain_data)
            return self._process_chain_data(frame)
        except Exception as exc:  # noqa: BLE001 - bubble up context via logger
            logger.error(
                "Failed to load option chain",
                symbol=self.symbol,
                expiry=target_expiry,
                error=str(exc),
            )
            return pd.DataFrame()

    def _process_chain_data(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Augment chain data with additional helper columns."""

        if frame.empty:
            return frame

        frame = frame.copy()
        frame["call_oi_change"] = frame.get("call_oi", 0) - frame.get("call_oi_prev", 0)
        frame["put_oi_change"] = frame.get("put_oi", 0) - frame.get("put_oi_prev", 0)
        call_oi = frame.get("call_oi", 1).replace(0, 1)
        frame["pcr"] = frame.get("put_oi", 0) / call_oi
        return frame.sort_values("strike")

    def get_atm_strike(self, spot_price: Optional[float] = None) -> float:
        """Return the at-the-money strike rounded to the contract strike gap."""

        if spot_price is None:
            quotes = openalgo.get_quotes(self.symbol, "NSE")
            spot_price = float(quotes.get("ltp", 0))

        strike_gap = self.contract_spec.get("strike_gap", 50)
        return round(spot_price / strike_gap) * strike_gap

    def get_strikes_by_delta(
        self,
        target_delta: float,
        option_type: str = "CE",
        expiry: Optional[str] = None,
    ) -> List[float]:
        """Return strikes closest to ``target_delta`` for the specified option type."""

        chain = self.get_chain(expiry)
        delta_column = "call_delta" if option_type.upper() == "CE" else "put_delta"

        if delta_column not in chain.columns:
            logger.warning("Delta column missing on option chain", column=delta_column)
            return []

        chain["delta_diff"] = (chain[delta_column] - target_delta).abs()
        results = chain.nsmallest(3, "delta_diff")["strike"].tolist()
        return results

    def get_iv_percentile(self, window_days: int = 30) -> float:
        """Placeholder for IV percentile calculation until historical data is wired."""

        return 50.0

    def get_option_greeks(self, strike: float, option_type: str, expiry: str) -> Dict[str, float]:
        """Return available greeks metrics for a specific contract."""

        chain = self.get_chain(expiry)
        row = chain[chain["strike"] == strike]
        if row.empty:
            return {}

        prefix = "call" if option_type.upper() == "CE" else "put"
        return {
            "delta": float(row[f"{prefix}_delta"].values[0]),
            "gamma": float(row[f"{prefix}_gamma"].values[0]),
            "theta": float(row[f"{prefix}_theta"].values[0]),
            "vega": float(row[f"{prefix}_vega"].values[0]),
            "iv": float(row[f"{prefix}_iv"].values[0]),
        }
