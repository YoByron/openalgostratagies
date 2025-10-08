"""Structured trade logging using loguru."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable

from loguru import logger

from config.settings import settings


@dataclass(slots=True)
class TradeRecord:
    timestamp: datetime
    symbol: str
    action: str
    quantity: int
    price: float
    order_id: str
    strategy: str
    metadata: Dict[str, object]


class TradeLogger:
    def __init__(self, log_dir: Path | None = None) -> None:
        self.log_dir = log_dir or settings.LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "trades.log"
        logger.add(self.log_file, rotation="1 week", enqueue=True, serialize=True)

    def log_trade(self, record: TradeRecord) -> None:
        logger.info("Trade executed", **asdict(record))

    def bulk_log(self, records: Iterable[TradeRecord]) -> None:
        for record in records:
            self.log_trade(record)
