"""Health check endpoints."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.redis_client import get_redis
from app.core.rabbitmq import get_channel

router = APIRouter()


@router.get("/")
async def health_check() -> JSONResponse:
    """Basic health check."""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
        }
    )


@router.get("/detailed")
async def detailed_health_check() -> JSONResponse:
    """Detailed health check with service status."""
    checks = {
        "redis": False,
        "rabbitmq": False,
    }

    # Check Redis
    try:
        redis = get_redis()
        await redis.ping()
        checks["redis"] = True
    except Exception:
        pass

    # Check RabbitMQ
    try:
        channel = get_channel()
        if channel and not channel.is_closed:
            checks["rabbitmq"] = True
    except Exception:
        pass

    # Determine overall status
    all_healthy = all(checks.values())
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if all_healthy else "degraded",
            "version": settings.APP_VERSION,
            "services": checks,
        }
    )
