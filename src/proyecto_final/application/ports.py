from __future__ import annotations

from typing import Protocol
from uuid import UUID

from proyecto_final.domain.order import Order


class OrderRepository(Protocol):
    def add(self, order: Order) -> None: ...

    def get(self, order_id: UUID) -> Order | None: ...

    def list(self) -> list[Order]: ...

    def update(self, order: Order) -> None: ...
