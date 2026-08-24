"""HTTP route modules."""

from proyecto_final.infrastructure.http.routes.auth_routes import router as auth_router
from proyecto_final.infrastructure.http.routes.order_routes import router as order_router

__all__ = ["auth_router", "order_router"]
