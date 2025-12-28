"""
Rate Limit Middleware - Aplica rate limiting a todos los requests.
"""

import time
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.rate_limiter import get_rate_limiter, RateLimitResult
from app.core.database import AsyncSessionLocal
from app.services.rate_limit_audit_service import RateLimitAuditService
from app.models import RateLimitAction


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware que aplica rate limiting a todos los requests.

    Features:
    - Token bucket algorithm
    - Auditoría automática
    - Headers de rate limit en response
    - Detección de actividad sospechosa
    """

    # Mapeo de endpoints a acciones
    ACTION_MAPPING = {
        "/api/v1/goals": RateLimitAction.API_CALL,
        "/api/v1/tasks": RateLimitAction.API_CALL,
        "/api/v1/code-snapshots": RateLimitAction.CODE_VALIDATION,
        "/api/v1/events": RateLimitAction.API_CALL,
    }

    # Endpoints excluidos de rate limiting
    EXCLUDED_PATHS = [
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
    ]

    def __init__(self, app: ASGIApp, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request con rate limiting."""

        # Skip si está deshabilitado
        if not self.enabled:
            return await call_next(request)

        # Skip paths excluidos
        if any(request.url.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return await call_next(request)

        # Obtener user_id (simplificado para POC)
        user_id = request.headers.get("X-User-ID", "anonymous")
        if user_id == "anonymous":
            # En producción, obtener del JWT token
            user_id = "test-user-123"

        # Determinar acción basada en el endpoint
        action = self._get_action_for_path(request.url.path)

        # Obtener rate limiter
        rate_limiter = await get_rate_limiter()

        # Start timer para response time
        start_time = time.time()

        # Check rate limit
        result: RateLimitResult = await rate_limiter.check_limit(
            user_id=user_id,
            action=action.value,
            tokens=1
        )

        # Registrar en auditoría (async en background)
        # En producción, usar background tasks de FastAPI
        await self._log_audit(
            request=request,
            user_id=user_id,
            action=action,
            result=result,
            start_time=start_time
        )

        # Si está bloqueado, retornar 429
        if not result.allowed:
            retry_after = int(result.retry_after_seconds or 60)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {retry_after} seconds.",
                    "retry_after": retry_after,
                    "limit": result.max_requests,
                    "window": result.window_seconds,
                    "current_count": result.current_count
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(result.max_requests),
                    "X-RateLimit-Remaining": str(result.tokens_available),
                    "X-RateLimit-Reset": str(int(time.time() + retry_after))
                }
            )

        # Procesar request
        response = await call_next(request)

        # Añadir headers de rate limit a la response
        response.headers["X-RateLimit-Limit"] = str(result.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(result.tokens_available)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time() + result.window_seconds)
        )

        return response

    def _get_action_for_path(self, path: str) -> RateLimitAction:
        """Determinar acción basada en el path."""
        for pattern, action in self.ACTION_MAPPING.items():
            if path.startswith(pattern):
                return action
        return RateLimitAction.API_CALL

    async def _log_audit(
        self,
        request: Request,
        user_id: str,
        action: RateLimitAction,
        result: RateLimitResult,
        start_time: float
    ) -> None:
        """Registrar en auditoría (background)."""
        try:
            async with AsyncSessionLocal() as db:
                audit_service = RateLimitAuditService(db)

                response_time_ms = (time.time() - start_time) * 1000

                await audit_service.log_request(
                    user_id=user_id,
                    endpoint=str(request.url.path),
                    method=request.method,
                    action=action,
                    rate_limit_result=result,
                    response_time_ms=response_time_ms,
                    http_status_code=200 if result.allowed else 429,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    metadata={
                        "query_params": dict(request.query_params),
                        "path_params": dict(request.path_params) if hasattr(request, 'path_params') else {}
                    }
                )
        except Exception as e:
            # No fallar el request si falla la auditoría
            print(f"Error logging rate limit audit: {e}")


# Dependency para usar en endpoints específicos
async def check_rate_limit(
    request: Request,
    user_id: str = "test-user-123",  # En producción: Depends(get_current_user_id)
    action: str = "api_call",
    tokens: int = 1
) -> RateLimitResult:
    """
    Dependency para verificar rate limit en endpoints específicos.

    Usage:
        @router.post("/expensive-operation")
        async def expensive_op(
            rate_limit: RateLimitResult = Depends(
                lambda req: check_rate_limit(req, action="embedding_generation", tokens=10)
            )
        ):
            # Endpoint que consume 10 tokens
            ...
    """
    rate_limiter = await get_rate_limiter()

    result = await rate_limiter.check_limit(
        user_id=user_id,
        action=action,
        tokens=tokens
    )

    if not result.allowed:
        retry_after = int(result.retry_after_seconds or 60)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "message": f"Too many {action} requests. Please try again in {retry_after} seconds.",
                "retry_after": retry_after,
                "limit": result.max_requests,
                "window": result.window_seconds
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(result.max_requests),
                "X-RateLimit-Remaining": str(result.tokens_available)
            }
        )

    return result
