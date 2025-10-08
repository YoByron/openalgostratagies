"""Application-wide logging setup."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from config.settings import settings


def configure_logging(log_level: str | None = None, log_file: Optional[Path] = None) -> None:
    logger.remove()

    level = (log_level or settings.LOG_LEVEL).upper()
    logger.add(sys.stderr, level=level, enqueue=True)

    target_file = log_file or Path(settings.LOG_FILE)
    target_file.parent.mkdir(parents=True, exist_ok=True)
    logger.add(target_file, level=level, rotation="1 day", retention="7 days", enqueue=True, backtrace=True, diagnose=False)
