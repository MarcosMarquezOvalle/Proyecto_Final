from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4


class OrderStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class OrderItem:
    sku: str
    quantity: int
    unit_price: Decimal

    def __post_init__(self) -> None:
        if not self.sku.strip():
            raise ValueError("sku cannot be empty")
        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")
        if self.unit_price <= 0:
            raise ValueError("unit_price must be greater than zero")

    @property
    def line_total(self) -> Decimal:
        return self.unit_price * Decimal(self.quantity)


@dataclass(frozen=True, slots=True)
class Order:
    id: UUID
    customer_id: str
    items: tuple[OrderItem, ...]
    created_at: datetime
    status: OrderStatus

    def __post_init__(self) -> None:
        if not self.customer_id.strip():
            raise ValueError("customer_id cannot be empty")
        if len(self.items) == 0:
            raise ValueError("order must contain at least one item")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone aware")

    @property
    def total_amount(self) -> Decimal:
        return sum((item.line_total for item in self.items), start=Decimal("0"))

    @classmethod
    def create(cls, customer_id: str, items: tuple[OrderItem, ...]) -> Order:
        return cls(
            id=uuid4(),
            customer_id=customer_id,
            items=items,
            created_at=datetime.now(UTC),
            status=OrderStatus.PENDING,
        )
