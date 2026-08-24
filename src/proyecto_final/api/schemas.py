from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from proyecto_final.domain.order import Order, OrderItem, OrderStatus


class OrderItemCreateRequest(BaseModel):
    sku: str = Field(min_length=1, examples=["SKU-001"])
    quantity: int = Field(gt=0, examples=[2])
    unit_price: Decimal = Field(gt=0, examples=["199.99"])


class CreateOrderRequest(BaseModel):
    customer_id: str = Field(min_length=1, examples=["CUST-123"])
    items: list[OrderItemCreateRequest] = Field(min_length=1)


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, examples=["admin"])
    password: str = Field(min_length=1, examples=["admin123"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sku: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal

    @classmethod
    def from_domain(cls, item: OrderItem) -> OrderItemResponse:
        return cls(
            sku=item.sku,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.line_total,
        )


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    customer_id: str
    items: list[OrderItemResponse]
    created_at: datetime
    status: OrderStatus
    total_amount: Decimal

    @classmethod
    def from_domain(cls, order: Order) -> OrderResponse:
        return cls(
            id=order.id,
            customer_id=order.customer_id,
            items=[OrderItemResponse.from_domain(item) for item in order.items],
            created_at=order.created_at,
            status=order.status,
            total_amount=order.total_amount,
        )


class ErrorResponse(BaseModel):
    detail: str
