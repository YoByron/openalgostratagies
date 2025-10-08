"""Validation helpers."""
from __future__ import annotations

from typing import Iterable, Mapping


def ensure_positive(value: float, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def ensure_non_empty(collection: Iterable, name: str) -> None:
    if not collection:
        raise ValueError(f"{name} cannot be empty")


def validate_required_keys(mapping: Mapping[str, object], keys: Iterable[str], context: str) -> None:
    missing = [key for key in keys if key not in mapping]
    if missing:
        raise KeyError(f"Missing keys in {context}: {', '.join(missing)}")
