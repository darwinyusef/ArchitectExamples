"""
Event model - Event Sourcing para trazabilidad completa.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, ForeignKey, Enum, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class EventType(str, enum.Enum):
    """Tipos de eventos del sistema."""
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"

    # Course events
    COURSE_CREATED = "course.created"
    COURSE_UPDATED = "course.updated"
    COURSE_COMPLETED = "course.completed"
    COURSE_ARCHIVED = "course.archived"

    # Goal events
    GOAL_CREATED = "goal.created"
    GOAL_UPDATED = "goal.updated"
    GOAL_STARTED = "goal.started"
    GOAL_COMPLETED = "goal.completed"
    GOAL_BLOCKED = "goal.blocked"

    # Task events
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_VALIDATED = "task.validated"
    TASK_FAILED = "task.failed"

    # Code events
    CODE_SUBMITTED = "code.submitted"
    CODE_REVIEWED = "code.reviewed"
    CODE_VALIDATED = "code.validated"

    # AI events
    AI_FEEDBACK_GENERATED = "ai.feedback.generated"
    AI_GOAL_SUGGESTED = "ai.goal.suggested"
    AI_VALIDATION_COMPLETED = "ai.validation.completed"

    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"


class Event(Base):
    """
    Event Sourcing - Todos los eventos del sistema.

    Estos eventos se almacenan en:
    1. PostgreSQL (para queries rápidas)
    2. Parquet files (para análisis histórico)
    3. RabbitMQ (para procesamiento asíncrono)

    Atributos:
        id: UUID único del evento
        event_type: Tipo de evento
        user_id: ID del usuario que generó el evento
        entity_type: Tipo de entidad afectada (goal, task, etc.)
        entity_id: ID de la entidad afectada
        payload: Datos del evento (JSON)
        event_metadata: Metadatos adicionales (IP, user agent, etc.)
        created_at: Timestamp del evento
        processed_at: Timestamp de procesamiento
        parquet_path: Path al archivo Parquet donde se guardó

    Relaciones:
        user: Usuario que generó el evento
    """

    __tablename__ = "events"

    # Primary Key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Event Info
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType),
        nullable=False,
        index=True
    )

    # Foreign Keys
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Entity Info (polymorphic)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=True, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=True, index=True)

    # Event Data (JSON)
    # Estructura: depende del event_type
    # Ejemplo goal.created: {
    #   "goal_id": "...",
    #   "title": "...",
    #   "description": "...",
    #   "ai_generated": true
    # }
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Event metadata (JSON)
    # Estructura: {
    #   "ip_address": "192.168.1.1",
    #   "user_agent": "...",
    #   "source": "vscode_extension",
    #   "version": "2.0.0"
    # }
    event_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Parquet Storage (path al archivo donde se guardó)
    parquet_path: Mapped[str] = mapped_column(String(500), nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="events")

    # Indexes compuestos para queries comunes
    __table_args__ = (
        Index("idx_events_user_created", "user_id", "created_at"),
        Index("idx_events_entity", "entity_type", "entity_id", "created_at"),
        Index("idx_events_type_created", "event_type", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Event(id={self.id}, type={self.event_type.value}, created_at={self.created_at})>"
