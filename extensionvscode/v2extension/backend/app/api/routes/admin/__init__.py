"""
Admin routes - Endpoints para administradores.
"""

from fastapi import APIRouter

from app.api.routes.admin import rate_limits

admin_router = APIRouter(prefix="/admin", tags=["admin"])

# Include sub-routers
admin_router.include_router(rate_limits.router, prefix="/rate-limits", tags=["rate-limits"])

__all__ = ["admin_router"]
