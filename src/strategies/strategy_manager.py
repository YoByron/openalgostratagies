"""Coordinate strategies with risk controls and order execution."""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Tuple

from loguru import logger

from config.settings import settings
from src.data.market_data_service import MarketDataService
from src.execution.order_manager import OrderManager, OrderRequest
from src.execution.position_tracker import PositionTracker
from src.risk.risk_controller import RiskController
from src.strategies.base_strategy import BaseStrategy, Signal


class StrategyManager:
    def __init__(
        self,
        order_manager: OrderManager,
        position_tracker: PositionTracker,
        risk_controller: RiskController,
        market_data_service: Optional[MarketDataService] = None,
        execution_mode: str = "paper",
    ) -> None:
        self.order_manager = order_manager
        self.position_tracker = position_tracker
        self.risk_controller = risk_controller
        self.market_data_service = market_data_service
        self.execution_mode = execution_mode
        self.strategies: Dict[str, BaseStrategy] = {}

    def register_strategy(self, strategy: BaseStrategy) -> None:
        self.strategies[strategy.name] = strategy

    def process_market_data(self, market_data: Dict) -> None:
        if not self.strategies:
            return

        positions_payload = [snapshot.as_dict() for snapshot in self.position_tracker.all_positions()]

        if self.market_data_service and not market_data.get("skip_market_refresh"):
            snapshot = self.market_data_service.snapshot(positions_payload)
            market_data.setdefault("spot_price", snapshot.spot_price)
            market_data.setdefault("portfolio_greeks", snapshot.portfolio_greeks)
            market_data.setdefault("option_chain", snapshot.option_chain)
            market_data.setdefault("timestamp", snapshot.timestamp)

        portfolio_value = market_data.get("portfolio_value")
        if portfolio_value:
            self.risk_controller.update_portfolio_value(float(portfolio_value))

        returns = market_data.get("returns")
        if returns is not None:
            self.risk_controller.update_returns(returns)

        exposures = market_data.get("portfolio_greeks", {})
        additional_margin = float(market_data.get("estimated_margin", 0.0))
        precomputed_signals = market_data.get("signals", {})

        for strategy in self.strategies.values():
            signal: Optional[Signal] = precomputed_signals.get(strategy.name)
            if signal is None:
                signal = strategy.generate_signal(market_data)
            if not signal:
                continue

            decision = self.risk_controller.evaluate(
                exposures=exposures,
                positions=positions_payload,
                additional_margin=additional_margin,
            )

            if not decision.approved:
                logger.warning(
                    "Risk controller blocked signal",
                    strategy=strategy.name,
                    reasons=decision.reasons,
                    var=decision.var,
                )
                continue

            strategy.log_signal(signal)
            self._execute_signal(strategy, signal, market_data)

    def _execute_signal(self, strategy: BaseStrategy, signal: Signal, market_data: Dict) -> None:
        if self.execution_mode == "dry_run":
            logger.info("Dry run signal", strategy=strategy.name, legs=signal.legs)
            return

        orders = self._build_order_requests(signal, market_data)
        for order in orders:
            try:
                self.order_manager.submit_order(order)
            except Exception as exc:  # noqa: BLE001
                logger.error("Order submission failed", strategy=strategy.name, error=str(exc))

    def _build_order_requests(self, signal: Signal, market_data: Dict) -> List[OrderRequest]:
        leg_prices = market_data.get("leg_prices", {})
        leg_symbols = market_data.get("leg_symbols", {})
        default_price = float(market_data.get("default_price", 0.0))
        product = market_data.get("product", "MIS")
        order_type = market_data.get("order_type", "LIMIT")

        requests: List[OrderRequest] = []
        for leg in signal.legs:
            key: Tuple = (leg.get("option_type"), leg.get("strike"), leg.get("expiry"))
            symbol = leg_symbols.get(key, signal.metadata.get("symbol") if signal.metadata else None)
            symbol = symbol or leg.get("symbol") or settings.SYMBOL
            price = float(leg.get("price", leg_prices.get(key, default_price)))
            quantity = int(leg.get("quantity", 1))

            requests.append(
                OrderRequest(
                    symbol=symbol,
                    exchange=leg.get("exchange", settings.EXCHANGE),
                    action=leg["action"],
                    quantity=quantity,
                    price=price,
                    product=leg.get("product", product),
                    order_type=leg.get("order_type", order_type),
                    trigger_price=leg.get("trigger_price"),
                )
            )
        return requests
