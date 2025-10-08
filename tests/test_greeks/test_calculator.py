from datetime import datetime, timedelta

import pytest

pytest.importorskip("py_vollib")

import pandas as pd

from src.greeks.calculator import GreeksCalculator, OptionContract


def test_year_fraction_positive():
    expiry = datetime.utcnow() + timedelta(days=7)
    fraction = GreeksCalculator.year_fraction(expiry)
    assert fraction > 0


def test_greeks_output_keys():
    contract = OptionContract("C", 20000, 20000, 0.02, 0.2, 0.05)
    greeks = GreeksCalculator.greeks(contract)
    assert {"delta", "gamma", "theta", "vega", "rho"}.issubset(greeks)
