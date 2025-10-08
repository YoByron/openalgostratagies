## Environment Setup

### Prerequisites
- Python 3.10+ (project validated on 3.13.7)
- pip with access to public PyPI
- Optional: virtual environment tooling (`venv`, `conda`, or `pipenv`)

### Installation Steps
1. **Clone or download the repository.**
2. **Create and activate a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate # macOS/Linux
   ```
3. **Install dependencies** from `requirements.txt`:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```
4. **Install optional analytics libraries** if needed for full functionality:
   - `vectorbt`, `quantstats`, `riskfolio-lib`, `ta-lib`

### Configuration
1. Copy `.env.example` to `.env` and populate OpenAlgo keys and environment flags:
   ```env
   OPENALGO_API_KEY=your-key
   OPENALGO_API_SECRET=your-secret
   OPENALGO_BASE_URL=https://api.openalgo.com
   TRADING_MODE=paper
   ```
2. Adjust risk parameters and trading metadata in `config/settings.py` and `config/strategy_config.py` as required.
3. For notebooks or scripts, ensure environment variables are loaded (e.g., via `python-dotenv`).
4. Run a deployment dry-run when ready:
   ```bash
   python scripts/deploy_service.py --mode paper
   ```
   Use `--mode live` for production checks once credentials are configured.

### Data Dependencies
- **Market Data:** Retrieved live from OpenAlgo via `OpenAlgoClient`, which now wraps the official `openalgo` SDK adapter; consider mock implementations for offline testing.
- **Historical Data:** Provide CSV/Parquet feeds under `data/` or integrate alternate data sources as needed.

### Upgrading Dependencies
- Re-run `python -m pip install -r requirements.txt --upgrade` after modifying dependencies.
- Lock versions via `requirements.txt` updates and validate with test suite (`python -m pytest`).
