"""Helper utilities used across modules."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional, Sequence


def chunked(sequence: Sequence, size: int) -> Iterable[Sequence]:
    for start in range(0, len(sequence), size):
        yield sequence[start : start + size]


def ensure_timezone(date: datetime, timezone: Optional[str] = None) -> datetime:
    if date.tzinfo is not None:
        return date
    if timezone is None:
        return date
    from zoneinfo import ZoneInfo

    return date.replace(tzinfo=ZoneInfo(timezone))


def flatten(nested: Iterable[Iterable]) -> list:
    return [item for inner in nested for item in inner]
