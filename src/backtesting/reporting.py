"""Utilities for packaging backtest analytics and reports."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pandas as pd

from src.backtesting.performance_metrics import PerformanceMetrics
from src.backtesting.vectorbt_engine import BacktestResult


@dataclass(slots=True)
class BacktestReport:
    """Container for summarized backtest analytics and exported artifacts."""

    stats: pd.Series
    report_path: Optional[Path]
    csv_path: Optional[Path]


def build_backtest_report(
    result: BacktestResult,
    metrics: PerformanceMetrics,
    name: str = "backtest",
    benchmark: Optional[pd.Series] = None,
    export_csv: bool = True,
) -> BacktestReport:
    """Generate QuantStats metrics, HTML report, and optional CSV summary."""

    returns = result.portfolio.returns()
    stats = metrics.summary(returns)

    csv_path: Optional[Path] = None
    if export_csv and metrics.output_dir:
        csv_path = metrics.output_dir / f"{name}_summary.csv"
        stats.to_csv(csv_path)

    report_path: Optional[Path] = None
    if metrics.output_dir:
        report_path = metrics.generate_report(returns, benchmark=benchmark, file_name=f"{name}.html")

    return BacktestReport(stats=stats, report_path=report_path, csv_path=csv_path)
