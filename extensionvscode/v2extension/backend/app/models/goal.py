"""
Goal model - Representa objetivos/metas de aprendizaje.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, DateTime, Text, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class GoalStatus(str, enum.Enum):
    """Estados posibles de un goal."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class GoalPriority(str, enum.Enum):
    """Prioridades de un goal."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Goal(Base):
    """
    Goal/Objetivo de aprendizaje.

    Atributos:
        id: UUID único del goal
        user_id: ID del usuario propietario
        course_id: ID del curso asociado (opcional)
        title: Título del goal
        description: Descripción detallada
        status: Estado del goal
        priority: Prioridad del goal
        progress_percentage: Progreso del goal (0-100)
        ai_generated: Si fue generado por IA
        validation_criteria: Criterios de validación
        goal_metadata: Datos adicionales
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
        started_at: Fecha de inicio
        completed_at: Fecha de completado
        due_date: Fecha límite

    Relaciones:
        owner: Usuario propietario
        course: Curso asociado
        tasks: Tasks del goal
        embeddings: Embeddings del goal
    """

    __tablename__ = "goals"

    # Primary Key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    course_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("courses.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Goal Info
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Status & Priority
    status: Mapped[GoalStatus] = mapped_column(
        Enum(GoalStatus),
        default=GoalStatus.PENDING,
        nullable=False,
        index=True
    )

    priority: Mapped[GoalPriority] = mapped_column(
        Enum(GoalPriority),
        default=GoalPriority.MEDIUM,
        nullable=False,
        index=True
    )

    # Progress
    progress_percentage: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # AI Info
    ai_generated: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Validation (JSON)
    # Estructura: {
    #   "criteria": ["Implementar función X", "Pasar tests", "Documentar"],
    #   "checklist": [{"item": "...", "completed": false}]
    # }
    validation_criteria: Mapped[dict] = mapped_column(JSON, nullable=True)

    # Goal metadata (JSON)
    # Estructura: {
    #   "tags": ["backend", "api"],
    #   "estimated_hours": 8,
    #   "actual_hours": 6.5,
    #   "difficulty": "medium",
    #   "resources": [...]
    # }
    goal_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=True)

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
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="goals")

    course: Mapped[Optional["Course"]] = relationship("Course", back_populates="goals")

    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="goal",
        cascade="all, delete-orphan"
    )

    embeddings: Mapped[List["Embedding"]] = relationship(
        "Embedding",
        foreign_keys="[Embedding.entity_id]",
        primaryjoin="and_(Goal.id == Embedding.entity_id, Embedding.entity_type == 'goal')",
        viewonly=True
    )

    def __repr__(self) -> str:
        return f"<Goal(id={self.id}, title={self.title}, status={self.status.value})>"
