import pandas as pd
import pytest

pytest.importorskip("vectorbt")

from src.backtesting.backtest_runner import BacktestRunner, BacktestConfig


def _make_signal_generator(entry_index: int):
    def generator(prices: pd.Series):
        entries = pd.Series(False, index=prices.index)
        exits = pd.Series(False, index=prices.index)
        entries.iloc[entry_index] = True
        exits.iloc[-1] = True
        return {
            "prices": prices,
            "entries": entries,
            "exits": exits,
        }

    return generator


@pytest.mark.scenario
@pytest.mark.backtest
def test_backtest_runner_multiple_scenarios(tmp_path):
    prices = pd.Series([100.0, 101.5, 103.0, 102.0, 104.5])

    runner = BacktestRunner(
        BacktestConfig(
            initial_capital=250_000,
            fees=0.0005,
            report_dir=tmp_path,
        )
    )

    summaries = []
    for idx in (0, 2):
        result = runner.run(prices, _make_signal_generator(idx))
        analysis = runner.analyze(result, report_name=f"scenario_{idx}.html")
        assert analysis["report_path"].exists()
        summaries.append(analysis["stats"])

    assert len(summaries) == 2
    assert all(summary.index.equals(summaries[0].index) for summary in summaries)
