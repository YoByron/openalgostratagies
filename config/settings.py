"""Global application configuration settings."""
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    LOG_DIR: Path = DATA_DIR / "logs"

    # OpenAlgo
    OPENALGO_API_KEY: str = Field(default="test-api-key")
    OPENALGO_HOST: str = "http://127.0.0.1:5000"
    BROKER_NAME: str = "zerodha"

    # Trading
    TRADING_MODE: Literal["paper", "live"] = "paper"
    SYMBOL: str = "NIFTY"
    EXCHANGE: str = "NFO"
    TIMEZONE: str = "Asia/Kolkata"

    # Risk Limits
    MAX_PORTFOLIO_DELTA: float = 100.0
    MAX_PORTFOLIO_GAMMA: float = 50.0
    MAX_PORTFOLIO_VEGA: float = 500.0
    MAX_POSITION_SIZE_PCT: float = 5.0
    MAX_DRAWDOWN_PCT: float = 10.0
    MAX_LOSS_PER_TRADE: float = 2000.0

    # Strategy
    DEFAULT_STRATEGY: str = "iron_condor"
    ENABLE_STOP_LOSS: bool = True
    ENABLE_TAKE_PROFIT: bool = True
    STOP_LOSS_PCT: float = 50.0
    TAKE_PROFIT_PCT: float = 50.0

    # Database
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    DATABASE_URL: str = "sqlite:///data/trading.db"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "data/logs/trading.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
