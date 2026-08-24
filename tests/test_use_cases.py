from __future__ import annotations

from decimal import Decimal

import pytest

from proyecto_final.adapters.in_memory_order_repository import InMemoryOrderRepository
from proyecto_final.application.use_cases import (
    CreateOrderCommand,
    CreateOrderItemInput,
    InvalidOrderTransitionError,
    OrderService,
)
from proyecto_final.domain.order import OrderStatus


def test_create_order_starts_pending_and_calculates_total() -> None:
    service = OrderService(repository=InMemoryOrderRepository())
    order = service.create_order(
        CreateOrderCommand(
            customer_id="CUST-001",
            items=(
                CreateOrderItemInput(sku="A", quantity=2, unit_price=Decimal("10.00")),
                CreateOrderItemInput(sku="B", quantity=1, unit_price=Decimal("2.50")),
            ),
        )
    )

    assert order.status == OrderStatus.PENDING
    assert order.total_amount == Decimal("22.50")


def test_invalid_transition_raises_error() -> None:
    service = OrderService(repository=InMemoryOrderRepository())
    order = service.create_order(
        CreateOrderCommand(
            customer_id="CUST-001",
            items=(CreateOrderItemInput(sku="A", quantity=1, unit_price=Decimal("10.00")),),
        )
    )

    with pytest.raises(InvalidOrderTransitionError):
        service.update_status(order.id, OrderStatus.SHIPPED)
