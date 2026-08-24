from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from proyecto_final.api.dependencies import get_order_service
from proyecto_final.api.schemas import (
    CreateOrderRequest,
    ErrorResponse,
    OrderResponse,
    UpdateOrderStatusRequest,
)
from proyecto_final.application.use_cases import (
    CreateOrderCommand,
    CreateOrderItemInput,
    InvalidOrderTransitionError,
    OrderNotFoundError,
    OrderService,
)

router = APIRouter(prefix="/orders", tags=["orders"])
OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}},
    summary="Crear una orden",
    description="Registra una nueva orden con sus ítems y la deja en estado pending.",
)
def create_order(
    payload: CreateOrderRequest,
    service: OrderServiceDep,
) -> OrderResponse:
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
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    return OrderResponse.from_domain(order)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    responses={404: {"model": ErrorResponse}},
    summary="Obtener una orden",
)
def get_order(
    order_id: UUID,
    service: OrderServiceDep,
) -> OrderResponse:
    try:
        order = service.get_order(order_id)
    except OrderNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    return OrderResponse.from_domain(order)


@router.get(
    "",
    response_model=list[OrderResponse],
    summary="Listar órdenes",
    description="Devuelve el listado de órdenes en orden descendente por fecha de creación.",
)
def list_orders(service: OrderServiceDep) -> list[OrderResponse]:
    return [OrderResponse.from_domain(order) for order in service.list_orders()]


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    summary="Actualizar estado",
)
def update_order_status(
    order_id: UUID,
    payload: UpdateOrderStatusRequest,
    service: OrderServiceDep,
) -> OrderResponse:
    try:
        order = service.update_status(order_id=order_id, new_status=payload.status)
    except OrderNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
    except InvalidOrderTransitionError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    return OrderResponse.from_domain(order)
