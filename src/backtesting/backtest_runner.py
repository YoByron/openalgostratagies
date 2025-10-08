"""High-level orchestration for running backtests."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Optional

import pandas as pd

from src.backtesting.performance_metrics import PerformanceMetrics
from src.backtesting.reporting import BacktestReport, build_backtest_report
from src.backtesting.vectorbt_engine import BacktestResult, VectorBTEngine


SignalGenerator = Callable[[pd.DataFrame], Dict[str, pd.Series]]


@dataclass(slots=True)
class BacktestConfig:
    initial_capital: float = 100_000.0
    fees: float = 0.0
    report_dir: Optional[Path] = None


class BacktestRunner:
    def __init__(self, config: BacktestConfig) -> None:
        self.config = config
        self.engine = VectorBTEngine(
            initial_capital=config.initial_capital,
            fees=config.fees,
        )
        self.metrics = PerformanceMetrics(config.report_dir)

    def run(self, data: pd.DataFrame, signal_generator: SignalGenerator) -> BacktestResult:
        signals = signal_generator(data)
        prices = signals["prices"]
        entries = signals["entries"]
        exits = signals["exits"]
        size = signals.get("size", 1)
        direction = signals.get("direction", "long")

        result = self.engine.run_from_signals(prices, entries, exits, size=size, direction=direction)
        return result

    def analyze(self, result: BacktestResult, benchmark: Optional[pd.Series] = None, report_name: str = "backtest_report.html") -> Dict[str, object]:
        returns = result.portfolio.returns()
        stats = self.metrics.summary(returns)
        report_path = None
        if self.config.report_dir:
            report_path = self.metrics.generate_report(returns, benchmark=benchmark, file_name=report_name)
        return {"stats": stats, "report_path": report_path}

    def build_report(
        self,
        result: BacktestResult,
        name: str = "backtest",
        benchmark: Optional[pd.Series] = None,
        export_csv: bool = True,
    ) -> BacktestReport:
        return build_backtest_report(result, self.metrics, name=name, benchmark=benchmark, export_csv=export_csv)
