"""
Task model - Representa tareas individuales dentro de un goal.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, Text, ForeignKey, Enum, JSON, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class TaskStatus(str, enum.Enum):
    """Estados posibles de una task."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskType(str, enum.Enum):
    """Tipos de task."""
    CODE = "code"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    RESEARCH = "research"
    REVIEW = "review"
    DEPLOYMENT = "deployment"
    OTHER = "other"


class Task(Base):
    """
    Task/Tarea individual.

    Atributos:
        id: UUID único de la task
        goal_id: ID del goal asociado
        user_id: ID del usuario asignado
        title: Título de la task
        description: Descripción detallada
        task_type: Tipo de task (code, doc, test, etc.)
        status: Estado de la task
        priority: Orden de prioridad (menor = más prioritario)
        estimated_hours: Horas estimadas
        actual_hours: Horas reales trabajadas
        validation_result: Resultado de validación por IA
        ai_feedback: Feedback generado por IA
        task_metadata: Datos adicionales
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
        started_at: Fecha de inicio
        completed_at: Fecha de completado

    Relaciones:
        goal: Goal al que pertenece
        assigned_to: Usuario asignado
        code_snapshots: Snapshots de código relacionados
        embeddings: Embeddings de la task
    """

    __tablename__ = "tasks"

    # Primary Key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Foreign Keys
    goal_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("goals.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Task Info
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Type & Status
    task_type: Mapped[TaskType] = mapped_column(
        Enum(TaskType),
        default=TaskType.CODE,
        nullable=False,
        index=True
    )

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        default=TaskStatus.TODO,
        nullable=False,
        index=True
    )

    # Priority (orden numérico, menor = más prioritario)
    priority: Mapped[int] = mapped_column(Integer, default=100, nullable=False)

    # Time Tracking
    estimated_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # AI Validation
    # Estructura: {
    #   "passed": true/false,
    #   "score": 0.95,
    #   "issues": [...],
    #   "validated_at": "2024-01-01T10:00:00Z"
    # }
    validation_result: Mapped[dict] = mapped_column(JSON, nullable=True)

    # AI Feedback (texto generado por LangGraph)
    ai_feedback: Mapped[str] = mapped_column(Text, nullable=True)

    # Task metadata (JSON)
    # Estructura: {
    #   "files": ["/path/to/file.py"],
    #   "commits": ["abc123"],
    #   "dependencies": ["task-id-1"],
    #   "tags": ["backend", "critical"]
    # }
    task_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    goal: Mapped["Goal"] = relationship("Goal", back_populates="tasks")

    assigned_to: Mapped["User"] = relationship("User", back_populates="tasks")

    code_snapshots: Mapped[List["CodeSnapshot"]] = relationship(
        "CodeSnapshot",
        back_populates="task",
        cascade="all, delete-orphan"
    )

    embeddings: Mapped[List["Embedding"]] = relationship(
        "Embedding",
        foreign_keys="[Embedding.entity_id]",
        primaryjoin="and_(Task.id == Embedding.entity_id, Embedding.entity_type == 'task')",
        viewonly=True
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title={self.title}, status={self.status.value})>"
