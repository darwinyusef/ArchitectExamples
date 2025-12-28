"""API router aggregation."""

from fastapi import APIRouter

from app.api import auth, websocket, health
from app.api.routes import goals, tasks, code_snapshots, events, users, courses
from app.api.routes.admin import admin_router

router = APIRouter()

# Include authentication and health
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(health.router, prefix="/health", tags=["Health"])

# Include CRUD endpoints
router.include_router(goals.router, prefix="/goals", tags=["Goals"])
router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
router.include_router(code_snapshots.router, prefix="/code-snapshots", tags=["Code Snapshots"])
router.include_router(events.router, prefix="/events", tags=["Events"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(courses.router, prefix="/courses", tags=["Courses"])

# Include admin endpoints
router.include_router(admin_router, tags=["Admin"])

# WebSocket endpoint is registered separately in main.py
# because it needs special handling
