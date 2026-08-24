from __future__ import annotations

from threading import Lock
from uuid import UUID

from proyecto_final.application.ports import OrderRepository
from proyecto_final.domain.order import Order


class InMemoryOrderRepository(OrderRepository):
    def __init__(self) -> None:
        self._orders: dict[UUID, Order] = {}
        self._lock = Lock()

    def add(self, order: Order) -> None:
        with self._lock:
            self._orders[order.id] = order

    def get(self, order_id: UUID) -> Order | None:
        return self._orders.get(order_id)

    def list(self) -> list[Order]:
        return sorted(self._orders.values(), key=lambda order: order.created_at, reverse=True)

    def update(self, order: Order) -> None:
        with self._lock:
            self._orders[order.id] = order
