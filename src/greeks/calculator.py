"""Utility helpers for computing option greeks with py_vollib."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from loguru import logger
from py_vollib import black_scholes
from py_vollib.black_scholes.greeks import analytical as greek_funcs


@dataclass(slots=True)
class OptionContract:
    """Container for the relevant option inputs."""

    option_type: str  # "C"/"P"
    spot: float
    strike: float
    time_to_expiry: float  # expressed in years
    volatility: float
    risk_free_rate: float


class GreeksCalculator:
    """Black-Scholes greeks and implied volatility utilities."""

    @staticmethod
    def year_fraction(
        expiry: datetime,
        valuation: Optional[datetime] = None,
        basis_days: float = 365.0,
    ) -> float:
        valuation_date = valuation or datetime.utcnow()
        delta_days = max((expiry - valuation_date).total_seconds(), 0) / 86400
        return max(delta_days / basis_days, 1e-10)

    @staticmethod
    def implied_volatility(
        option_price: float,
        option_type: str,
        spot: float,
        strike: float,
        time_to_expiry: float,
        risk_free_rate: float,
    ) -> Optional[float]:
        flag = GreeksCalculator._flag(option_type)
        try:
            return black_scholes.implied_volatility.implied_volatility(
                option_price,
                spot,
                strike,
                time_to_expiry,
                risk_free_rate,
                flag,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Implied volatility calculation failed", error=str(exc))
            return None

    @staticmethod
    def greeks(contract: OptionContract) -> Dict[str, float]:
        flag = GreeksCalculator._flag(contract.option_type)
        return {
            "delta": greek_funcs.delta(flag, contract.spot, contract.strike, contract.time_to_expiry, contract.risk_free_rate, contract.volatility),
            "gamma": greek_funcs.gamma(flag, contract.spot, contract.strike, contract.time_to_expiry, contract.risk_free_rate, contract.volatility),
            "theta": greek_funcs.theta(flag, contract.spot, contract.strike, contract.time_to_expiry, contract.risk_free_rate, contract.volatility),
            "vega": greek_funcs.vega(flag, contract.spot, contract.strike, contract.time_to_expiry, contract.risk_free_rate, contract.volatility),
            "rho": greek_funcs.rho(flag, contract.spot, contract.strike, contract.time_to_expiry, contract.risk_free_rate, contract.volatility),
        }

    @staticmethod
    def _flag(option_type: str) -> str:
        normalized = option_type.strip().lower()
        if normalized not in {"c", "call", "p", "put"}:
            raise ValueError(f"Unsupported option type: {option_type}")
        return "c" if normalized.startswith("c") else "p"
