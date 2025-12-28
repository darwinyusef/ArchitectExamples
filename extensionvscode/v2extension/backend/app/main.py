"""FastAPI application entry point with WebSocket support."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db
from app.core.redis_client import init_redis, close_redis
from app.core.rabbitmq import init_rabbitmq, close_rabbitmq
from app.api import router as api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    # Startup
    logger.info("Starting AI Goals Tracker Backend...")

    # Initialize database
    await init_db()
    logger.info("✓ Database initialized")

    # Initialize Redis
    await init_redis()
    logger.info("✓ Redis connected")

    # Initialize RabbitMQ
    await init_rabbitmq()
    logger.info("✓ RabbitMQ connected")

    logger.info("🚀 Application ready!")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await close_rabbitmq()
    await close_redis()
    logger.info("✓ Cleanup completed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Real-time AI-powered goals tracking system with LangGraph agents",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
from app.middleware.rate_limit_middleware import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware, enabled=True)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Include WebSocket route separately
from app.api.websocket import router as ws_router
app.include_router(ws_router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint for monitoring."""
    # TODO: Add actual health checks for DB, Redis, RabbitMQ
    return JSONResponse(
        content={
            "status": "healthy",
            "version": settings.APP_VERSION,
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )
