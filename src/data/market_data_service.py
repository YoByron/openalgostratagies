"""Market data service collecting quotes, option chains, and greeks."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Iterable, Optional

import pandas as pd

from config.settings import settings
from src.data.openalgo_client import openalgo
from src.data.options_chain import OptionsChainHandler
from src.greeks.calculator import GreeksCalculator, OptionContract
from src.utils.helpers import ensure_timezone


@dataclass(slots=True)
class MarketDataSnapshot:
    timestamp: datetime
    spot_price: float
    portfolio_greeks: Dict[str, float]
    option_chain: Optional[pd.DataFrame]


class MarketDataService:
    def __init__(
        self,
        symbol: str = "NIFTY",
        exchange: str = "NFO",
    ) -> None:
        self.symbol = symbol
        self.exchange = exchange
        self.chain_handler = OptionsChainHandler(symbol)
        self.greeks_calculator = GreeksCalculator()

    def fetch_spot_price(self) -> float:
        quotes = openalgo.get_quotes(self.symbol, self.exchange)
        return float(quotes.get("ltp", 0.0))

    def fetch_option_chain(self, expiry: Optional[str] = None) -> pd.DataFrame:
        return self.chain_handler.get_chain(expiry)

    def compute_greeks_snapshot(
        self,
        option_positions: Iterable[Dict[str, object]],
        spot_price: float,
        valuation_time: Optional[datetime] = None,
    ) -> Dict[str, float]:
        valuation_time = ensure_timezone(valuation_time or datetime.utcnow(), settings.TIMEZONE)
        greeks_totals = {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0}

        for pos in option_positions:
            option_type = str(pos.get("option_type", "CE")).upper()
            flag = "C" if option_type in {"CE", "C", "CALL"} else "P"
            strike = float(pos.get("strike", 0.0))
            expiry = pos.get("expiry")
            expiry_dt = valuation_time + timedelta(days=7)
            if expiry:
                try:
                    expiry_dt = ensure_timezone(datetime.fromisoformat(str(expiry)), settings.TIMEZONE)
                except ValueError:
                    pass
            time_to_expiry = max(
                GreeksCalculator.year_fraction(expiry_dt, valuation_time),
                1e-6,
            )
            volatility = float(pos.get("iv", 0.2))
            risk_free_rate = float(pos.get("risk_free_rate", 0.05))
            qty = float(pos.get("quantity", 0.0))
            if strike <= 0 or qty == 0:
                continue
            contract = OptionContract(flag, spot_price, strike, time_to_expiry, volatility, risk_free_rate)
            greeks = self.greeks_calculator.greeks(contract)
            for key in greeks_totals:
                greeks_totals[key] += greeks.get(key, 0.0) * qty
        return greeks_totals

    def snapshot(self, option_positions: Iterable[Dict[str, object]]) -> MarketDataSnapshot:
        spot_price = self.fetch_spot_price()
        option_chain = self.fetch_option_chain()
        greeks = self.compute_greeks_snapshot(option_positions, spot_price)
        return MarketDataSnapshot(
            timestamp=datetime.utcnow(),
            spot_price=spot_price,
            portfolio_greeks=greeks,
            option_chain=option_chain,
        )
