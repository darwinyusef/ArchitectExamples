"""
Service Layer - Business logic for AI Goals Tracker.

Los servicios encapsulan la lógica de negocio y operaciones CRUD.
Cada servicio maneja:
- Validación de datos
- Operaciones de base de datos
- Generación de embeddings para RAG
- Persistencia triple (PostgreSQL + Parquet + RabbitMQ)
"""

from app.services.goal_service import GoalService
from app.services.task_service import TaskService
from app.services.code_snapshot_service import CodeSnapshotService
from app.services.event_service import EventService
from app.services.user_service import UserService
from app.services.course_service import CourseService

__all__ = [
    "GoalService",
    "TaskService",
    "CodeSnapshotService",
    "EventService",
    "UserService",
    "CourseService",
]
