"""Track open positions and reconcile with broker state."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from loguru import logger


@dataclass(slots=True)
class PositionSnapshot:
    symbol: str
    quantity: int
    average_price: float
    product: str
    pnl: float = 0.0

    def as_dict(self) -> Dict[str, object]:
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "average_price": self.average_price,
            "product": self.product,
            "pnl": self.pnl,
        }


class PositionTracker:
    def __init__(self) -> None:
        self.positions: Dict[str, PositionSnapshot] = {}

    def sync_from_broker(self, broker_positions: Iterable[Dict[str, object]]) -> None:
        self.positions.clear()
        for entry in broker_positions:
            symbol = str(entry.get("symbol"))
            self.positions[symbol] = PositionSnapshot(
                symbol=symbol,
                quantity=int(entry.get("quantity", 0)),
                average_price=float(entry.get("average_price", 0.0)),
                product=str(entry.get("product", "MIS")),
                pnl=float(entry.get("pnl", 0.0)),
            )
        logger.debug("Positions synced", count=len(self.positions))

    def update_mark_to_market(self, symbol: str, last_price: float) -> None:
        position = self.positions.get(symbol)
        if not position:
            return
        position.pnl = (last_price - position.average_price) * position.quantity

    def get_position(self, symbol: str) -> Optional[PositionSnapshot]:
        return self.positions.get(symbol)

    def all_positions(self) -> List[PositionSnapshot]:
        return list(self.positions.values())

    def net_quantity(self, symbol: str) -> int:
        snapshot = self.positions.get(symbol)
        return snapshot.quantity if snapshot else 0
