from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from uuid import UUID

from proyecto_final.application.ports import OrderRepository
from proyecto_final.domain.order import Order, OrderItem, OrderStatus


class OrderNotFoundError(Exception):
    def __init__(self, order_id: UUID) -> None:
        self.order_id = order_id
        super().__init__(f"order {order_id} was not found")


class InvalidOrderTransitionError(Exception):
    def __init__(self, current_status: OrderStatus, requested_status: OrderStatus) -> None:
        self.current_status = current_status
        self.requested_status = requested_status
        super().__init__(f"cannot transition from {current_status} to {requested_status}")


@dataclass(frozen=True, slots=True)
class CreateOrderItemInput:
    sku: str
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True, slots=True)
class CreateOrderCommand:
    customer_id: str
    items: tuple[CreateOrderItemInput, ...]


class OrderService:
    _allowed_transitions: dict[OrderStatus, set[OrderStatus]] = {
        OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
        OrderStatus.CONFIRMED: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
        OrderStatus.SHIPPED: set(),
        OrderStatus.CANCELLED: set(),
    }

    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def create_order(self, command: CreateOrderCommand) -> Order:
        order_items = tuple(
            OrderItem(sku=item.sku, quantity=item.quantity, unit_price=item.unit_price)
            for item in command.items
        )
        order = Order.create(customer_id=command.customer_id, items=order_items)
        self._repository.add(order)
        return order

    def get_order(self, order_id: UUID) -> Order:
        order = self._repository.get(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order

    def list_orders(self) -> list[Order]:
        return self._repository.list()

    def update_status(self, order_id: UUID, new_status: OrderStatus) -> Order:
        order = self.get_order(order_id)
        if new_status == order.status:
            return order
        allowed = self._allowed_transitions[order.status]
        if new_status not in allowed:
            raise InvalidOrderTransitionError(order.status, new_status)
        updated_order = replace(order, status=new_status)
        self._repository.update(updated_order)
        return updated_order
