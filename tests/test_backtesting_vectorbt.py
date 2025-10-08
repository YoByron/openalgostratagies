import pytest

pytest.importorskip("vectorbt")

import pandas as pd

from src.backtesting.vectorbt_engine import VectorBTEngine
from src.backtesting.backtest_runner import BacktestRunner, BacktestConfig


def test_vectorbt_engine_run_from_signals():
    prices = pd.Series([100, 102, 101, 105])
    entries = pd.Series([True, False, False, False])
    exits = pd.Series([False, False, False, True])

    engine = VectorBTEngine(initial_capital=10000, fees=0.001)
    result = engine.run_from_signals(prices, entries, exits)
    assert hasattr(result, "portfolio")
    assert hasattr(result, "stats")


def test_backtest_runner_run_and_analyze(tmp_path):
    prices = pd.Series([100, 101, 102, 103, 104])

    def signal_generator(data):
        return {
            "prices": data,
            "entries": pd.Series([True, False, False, False, False]),
            "exits": pd.Series([False, False, False, False, True]),
        }

    runner = BacktestRunner(BacktestConfig(initial_capital=50_000, fees=0.0, report_dir=tmp_path))
    result = runner.run(prices, signal_generator)
    analysis = runner.analyze(result, report_name="test_report.html")

    assert "stats" in analysis
    assert analysis["report_path"].exists()


def test_backtest_runner_build_report(tmp_path):
    prices = pd.Series([100, 101, 103, 102, 104])

    def signal_generator(data):
        entries = pd.Series(False, index=data.index)
        exits = pd.Series(False, index=data.index)
        entries.iloc[1] = True
        exits.iloc[-1] = True
        return {"prices": data, "entries": entries, "exits": exits}

    runner = BacktestRunner(BacktestConfig(initial_capital=75_000, report_dir=tmp_path))
    result = runner.run(prices, signal_generator)
    report = runner.build_report(result, name="smoke", export_csv=True)

    assert report.report_path is not None and report.report_path.exists()
    assert report.csv_path is not None and report.csv_path.exists()
    assert any("sharpe" in idx.lower() for idx in report.stats.index)
