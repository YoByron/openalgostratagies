## Testing & Quality Assurance

### Test Suite Overview
- **Unit tests** validate individual modules (risk checks, strategy leg creation, greeks calculations).
- **Integration tests** simulate end-to-end flows using stubbed OpenAlgo responses to ensure orchestration correctness.
- **Backtesting tests** (marked `@pytest.mark.backtest`) validate VectorBT/QuantStats flows and automatically skip if VectorBT is unavailable.

### Running Tests
```bash
python -m pytest
```

Use `-k` to target subsets (e.g., `python -m pytest -k risk`) and `-s` for verbose logging when debugging.
Apply markers for focused runs:
```bash
python -m pytest -m scenario
python -m pytest -m "backtest and not scenario"
```

### Test Data & Fixtures
- Tests rely on inline fixtures and monkeypatched functions to avoid live API calls.
- Scenario tests in `tests/test_integration/test_strategy_flow.py` and `tests/test_integration/test_backtest_scenarios.py` exercise `StrategyManager`, `RiskController`, and backtest orchestration together.

### Coverage & Linting
- Run `pytest --cov=src` once coverage configuration is added.
- Lint via `ruff check .` and type-check with `mypy src` (see `.github/workflows/ci.yml`).

### CI Recommendations
- Run the full pytest suite on every pull request (configured in `.github/workflows/ci.yml`).
- Cache Python dependencies to accelerate builds.
- Surface loguru outputs and pytest warnings in CI logs for fast diagnosis.
- Gate merges on Ruff lint, mypy type checks, and pytest success for consistent quality.

### Optional Dependency Strategy
- Wrap imports for optional libraries (`vectorbt`, `quantstats`, `riskfolio-lib`) with `pytest.importorskip` in tests and runtime guards in code to maintain lean environments.
