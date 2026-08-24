"""HTTP dependency providers for FastAPI routes."""

from proyecto_final.infrastructure.http.dependencies.order_dependencies import (
    build_default_repository,
    get_api_key_validator,
    get_order_service,
)

__all__ = ["build_default_repository", "get_api_key_validator", "get_order_service"]
