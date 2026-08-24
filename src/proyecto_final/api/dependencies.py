from __future__ import annotations

import secrets
from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

from proyecto_final.adapters.sqlite_order_repository import SqliteOrderRepository
from proyecto_final.application.ports import OrderRepository
from proyecto_final.application.use_cases import OrderService

api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)


def get_order_service(request: Request) -> OrderService:
    repository = request.app.state.order_repository
    return OrderService(repository)


def get_api_key_validator() -> Callable[..., None]:
    def validate_api_key(
        request: Request,
        api_key: str | None = Depends(api_key_scheme),
    ) -> None:
        expected_api_key: str = request.app.state.api_key
        if api_key is None or not secrets.compare_digest(api_key, expected_api_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key",
            )

    return validate_api_key


def build_default_repository(database_path: str | None = None) -> OrderRepository:
    return SqliteOrderRepository(database_path=database_path)
