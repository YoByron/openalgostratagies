"""Monitor SPAN and exposure margins."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Optional

from src.data.openalgo_client import openalgo


@dataclass(slots=True)
class MarginCheckResult:
    required_margin: float
    available_margin: float
    deficit: float
    is_within_limit: bool


class MarginMonitor:
    def __init__(
        self,
        max_utilization_pct: float = 0.8,
        margin_fetcher: Optional[Callable[[Iterable[Mapping[str, object]]], Mapping[str, object]]] = None,
        funds_fetcher: Optional[Callable[[], Mapping[str, object]]] = None,
    ) -> None:
        self.max_utilization_pct = max_utilization_pct
        self._margin_fetcher = margin_fetcher or (lambda positions: openalgo.get_margins(list(positions)))
        self._funds_fetcher = funds_fetcher or openalgo.get_funds

    def check_positions(self, positions: Iterable[Mapping[str, object]]) -> MarginCheckResult:
        margin_data = self._margin_fetcher(list(positions))
        required_margin = float(margin_data.get("span_margin", 0.0))

        funds = self._funds_fetcher()
        available = float(funds.get("available_margin", funds.get("net", 0.0)))

        deficit = max(required_margin - available, 0.0)
        limit = available * self.max_utilization_pct
        within = required_margin <= limit
        return MarginCheckResult(
            required_margin=required_margin,
            available_margin=available,
            deficit=deficit,
            is_within_limit=within,
        )

    def has_sufficient_margin(self, additional_requirement: float) -> bool:
        funds = self._funds_fetcher()
        available = float(funds.get("available_margin", funds.get("net", 0.0)))
        limit = available * self.max_utilization_pct
        return additional_requirement <= limit
