from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from proyecto_final.application.use_cases import (
    CreateOrderCommand,
    CreateOrderItemInput,
    OrderNotFoundError,
    OrderService,
)
from proyecto_final.infrastructure.http.dependencies.order_dependencies import get_order_service
from proyecto_final.infrastructure.http.schemas.order_schemas import (
    CreateOrderRequest,
    CreateOrderResponse,
    ErrorResponse,
    OrderResponse,
    UpdateOrderStatusRequest,
)

router = APIRouter(tags=["orders"])
OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]


@router.post(
    "/orders",
    response_model=CreateOrderResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    summary="Crear orden",
    description="Crea una nueva orden con sus elementos y calcula el total.",
)
def create_order(
    payload: CreateOrderRequest,
    service: OrderServiceDep,
) -> CreateOrderResponse:
    command = CreateOrderCommand(
        customer_id=payload.customer_id,
        items=tuple(
            CreateOrderItemInput(
                sku=item.sku,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in payload.items
        ),
    )
    try:
        order = service.create_order(command)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return CreateOrderResponse.model_validate(order)


@router.get(
    "/orders",
    response_model=list[OrderResponse],
    summary="Listar órdenes",
    description="Devuelve todas las órdenes persistidas en la base de datos.",
)
def list_orders(service: OrderServiceDep) -> list[OrderResponse]:
    orders = service.list_orders()
    return [OrderResponse.from_domain(order) for order in orders]


@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Obtener orden",
    description="Obtiene una orden por su identificador.",
)
def get_order(
    order_id: UUID,
    service: OrderServiceDep,
) -> OrderResponse:
    try:
        order = service.get_order(order_id)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return OrderResponse.from_domain(order)


@router.patch(
    "/orders/{order_id}/status",
    response_model=OrderResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Actualizar estado de la orden",
    description="Actualiza el estado de una orden validando la transición permitida.",
)
def update_order_status(
    order_id: UUID,
    payload: UpdateOrderStatusRequest,
    service: OrderServiceDep,
) -> OrderResponse:
    try:
        order = service.update_status(order_id, payload.status)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return OrderResponse.from_domain(order)
