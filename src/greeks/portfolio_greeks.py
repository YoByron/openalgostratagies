"""Portfolio level greeks aggregation utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, MutableMapping, Optional

from config.strategy_config import CONTRACT_SPECS


@dataclass(slots=True)
class GreekExposure:
    delta: float = 0.0
    gamma: float = 0.0
    theta: float = 0.0
    vega: float = 0.0
    rho: float = 0.0

    def as_dict(self) -> MutableMapping[str, float]:
        return {
            "delta": self.delta,
            "gamma": self.gamma,
            "theta": self.theta,
            "vega": self.vega,
            "rho": self.rho,
        }


class PortfolioGreeksAggregator:
    """Aggregates per-leg greeks into portfolio exposures."""

    def __init__(self, symbol: str = "NIFTY") -> None:
        self.symbol = symbol

    def aggregate(
        self,
        leg_greeks: Iterable[Mapping[str, float]],
        quantities: Iterable[int],
        sides: Optional[Iterable[int]] = None,
        lot_size: Optional[int] = None,
    ) -> GreekExposure:
        exposure = GreekExposure()
        resolved_lot = lot_size or CONTRACT_SPECS.get(self.symbol, {}).get("lot_size", 1)

        greek_list = list(leg_greeks)
        quantity_list = list(quantities)
        if len(greek_list) != len(quantity_list):
            raise ValueError("Quantities length must match leg greeks length")

        sides_list = list(sides) if sides is not None else [1] * len(greek_list)
        if len(sides_list) != len(greek_list):
            raise ValueError("Sides length must match leg greeks length")

        for index, greek in enumerate(greek_list):
            qty = quantity_list[index] * resolved_lot
            sign = sides_list[index]
            exposure.delta += greek.get("delta", 0.0) * qty * sign
            exposure.gamma += greek.get("gamma", 0.0) * qty * sign
            exposure.theta += greek.get("theta", 0.0) * qty * sign
            exposure.vega += greek.get("vega", 0.0) * qty * sign
            exposure.rho += greek.get("rho", 0.0) * qty * sign
        return exposure
