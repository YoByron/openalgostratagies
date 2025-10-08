"""Performance analytics integrating QuantStats and custom KPIs."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import quantstats as qs


class PerformanceMetrics:
    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = output_dir
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def summary(self, returns: pd.Series) -> pd.Series:
        qs.extend_pandas()
        return returns.stats()

    def generate_report(self, returns: pd.Series, benchmark: Optional[pd.Series] = None, file_name: str = "report.html") -> Path:
        if not self.output_dir:
            raise ValueError("Output directory must be set to generate report")
        output_path = self.output_dir / file_name
        qs.reports.html(returns, benchmark=benchmark, output=output_path)
        return output_path
