"""Deployment helper orchestrating preflight checks for trading services."""
from __future__ import annotations

import argparse
import sys
from typing import List

from loguru import logger

from config.settings import settings
from src.data.openalgo_client import openalgo
from src.utils.logger import configure_logging


def _validate_environment() -> List[str]:
    missing = []
    if not settings.OPENALGO_API_KEY or settings.OPENALGO_API_KEY == "demo-api-key":
        missing.append("OPENALGO_API_KEY")
    if not settings.OPENALGO_HOST:
        missing.append("OPENALGO_HOST")
    return missing


def _check_feed_connectivity() -> bool:
    connected = False
    try:
        connected = openalgo.connect_feed()
        return connected
    finally:
        if connected:
            openalgo.disconnect_feed()


def _check_funds() -> None:
    try:
        funds = openalgo.get_funds()
        available = funds.get("available_margin")
        logger.info("Broker funds check", available_margin=available)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Unable to fetch broker funds", error=str(exc))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deployment preflight checks for trading services.")
    parser.add_argument("--mode", choices=["paper", "live"], default="paper", help="Deployment mode")
    args = parser.parse_args()

    configure_logging()
    logger.info("Starting deployment checks", mode=args.mode)

    missing_env = _validate_environment()
    if missing_env:
        logger.warning("Missing critical environment variables", variables=missing_env)

    _check_funds()

    feed_ok = _check_feed_connectivity()
    if not feed_ok:
        logger.warning("Feed connectivity test failed")
    else:
        logger.info("Feed connectivity verified")

    if args.mode == "live" and settings.TRADING_MODE != "live":
        logger.warning("TRADING_MODE is not set to 'live' for live deployment")

    logger.info(
        "Next steps",
        paper_loop="python scripts/paper_trading_loop.py",
        strategy_demo="python scripts/run_paper_trading.py",
    )

    if missing_env or not feed_ok:
        logger.error("Deployment checks completed with warnings")
        return 1

    logger.success("Deployment preflight completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
