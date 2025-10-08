from src.risk.risk_limits import RiskLimitsChecker, RiskThresholds


def test_greeks_within_limits():
    thresholds = RiskThresholds(100, 50, 500, 0.05, 10, 2000)
    checker = RiskLimitsChecker(thresholds)
    exposures = {"delta": 90, "gamma": 40, "vega": 300}
    assert checker.greeks_within_limits(exposures)


def test_drawdown_limit():
    thresholds = RiskThresholds(100, 50, 500, 0.05, 10, 2000)
    checker = RiskLimitsChecker(thresholds)
    assert not checker.drawdown_within_limit(12)
