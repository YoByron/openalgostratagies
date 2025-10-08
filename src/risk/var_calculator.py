"""Value at Risk calculation utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd


VaRMethod = Literal["historical", "variance_covariance"]


@dataclass(slots=True)
class VaRConfig:
    confidence_level: float = 0.95
    method: VaRMethod = "historical"


class VaRCalculator:
    def __init__(self, config: VaRConfig) -> None:
        self.config = config

    def calculate(self, returns: pd.Series, portfolio_value: float) -> float:
        if returns.empty:
            return 0.0

        if self.config.method == "historical":
            return self._historical_var(returns, portfolio_value)
        if self.config.method == "variance_covariance":
            return self._variance_covariance_var(returns, portfolio_value)
        raise ValueError(f"Unsupported VaR method: {self.config.method}")

    def _historical_var(self, returns: pd.Series, portfolio_value: float) -> float:
        percentile = 100 * (1 - self.config.confidence_level)
        loss_quantile = np.percentile(returns, percentile)
        return -loss_quantile * portfolio_value

    def _variance_covariance_var(self, returns: pd.Series, portfolio_value: float) -> float:
        mean = returns.mean()
        std = returns.std(ddof=1)
        z_score = self._z_score(self.config.confidence_level)
        var = (mean - z_score * std) * portfolio_value
        return max(-var, 0.0)

    @staticmethod
    def _z_score(confidence_level: float) -> float:
        from scipy.stats import norm

        return norm.ppf(confidence_level)
