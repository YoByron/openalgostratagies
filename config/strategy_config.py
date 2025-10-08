"""Strategy configuration and market metadata."""
from enum import Enum
from typing import Any, Dict


class StrategyType(Enum):
    """Enumerates supported options strategy identifiers."""

    IRON_CONDOR = "iron_condor"
    STRADDLE = "straddle"
    STRANGLE = "strangle"
    BUTTERFLY = "butterfly"
    CALENDAR_SPREAD = "calendar_spread"
    DELTA_NEUTRAL = "delta_neutral"


STRATEGY_PARAMS: Dict[str, Dict[str, Any]] = {
    "iron_condor": {
        "call_width": 200,
        "put_width": 200,
        "target_delta": 0.30,
        "dte_entry": 7,
        "dte_exit": 2,
        "profit_target": 0.50,
        "stop_loss": 2.0,
        "max_positions": 3,
    },
    "straddle": {
        "direction": "long",
        "atm_offset": 0,
        "dte_entry": 7,
        "dte_exit": 2,
        "profit_target": 0.30,
        "stop_loss": 0.50,
        "iv_percentile_min": 30,
    },
    "strangle": {
        "direction": "long",
        "call_delta": 0.30,
        "put_delta": 0.30,
        "dte_entry": 7,
        "dte_exit": 2,
        "profit_target": 0.40,
        "stop_loss": 0.60,
        "iv_percentile_min": 40,
    },
    "butterfly": {
        "wing_width": 100,
        "atm_offset": 0,
        "dte_entry": 7,
        "dte_exit": 2,
        "profit_target": 0.50,
        "stop_loss": 1.0,
    },
    "calendar_spread": {
        "strike_selection": "atm",
        "front_month_dte": 7,
        "back_month_dte": 30,
        "profit_target": 0.30,
        "stop_loss": 0.50,
    },
    "delta_neutral": {
        "delta_threshold": 5,
        "rebalance_frequency": "daily",
        "target_allocation": {
            "calls": 0.5,
            "puts": 0.5,
        },
    },
}


MARKET_HOURS = {
    "pre_market_start": "09:00",
    "market_open": "09:15",
    "market_close": "15:30",
    "post_market_end": "16:00",
}


WEEKLY_EXPIRY = {
    "NIFTY": "Thursday",
    "BANKNIFTY": "Wednesday",
    "FINNIFTY": "Tuesday",
    "MIDCPNIFTY": "Monday",
}


CONTRACT_SPECS = {
    "NIFTY": {
        "lot_size": 50,
        "tick_size": 0.05,
        "strike_gap": 50,
    },
    "BANKNIFTY": {
        "lot_size": 15,
        "tick_size": 0.05,
        "strike_gap": 100,
    },
    "FINNIFTY": {
        "lot_size": 40,
        "tick_size": 0.05,
        "strike_gap": 50,
    },
}
