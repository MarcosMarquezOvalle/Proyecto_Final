from __future__ import annotations

import os

from fastapi import Depends, FastAPI

from proyecto_final.api.auth_routes import router as auth_router
from proyecto_final.api.dependencies import build_default_repository
from proyecto_final.api.routes import router as order_router
from proyecto_final.application.ports import OrderRepository
from proyecto_final.infrastructure.security.jwt_auth import get_current_user


def create_app(
    repository: OrderRepository | None = None,
    api_key: str | None = None,
    database_path: str | None = None,
) -> FastAPI:
    app = FastAPI(
        title="Orders Service",
        summary="Servicio de órdenes con arquitectura hexagonal.",
        description=(
            "API para crear, consultar y actualizar órdenes. "
            "Incluye autenticación JWT y documentación OpenAPI."
        ),
        version="1.0.0",
    )

    resolved_database_path = database_path or os.getenv("ORDER_DB_PATH")

    app.state.order_repository = repository or build_default_repository(
        database_path=resolved_database_path
    )
    app.state.api_key = api_key or os.getenv("ORDER_API_KEY", "change-me")
    app.state.database_path = resolved_database_path

    app.include_router(auth_router)
    app.include_router(
        order_router,
        dependencies=[Depends(get_current_user)],
    )
    return app


app = create_app()
