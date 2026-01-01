"""
Course model - Representa cursos o proyectos de aprendizaje.
"""

from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class CourseStatus(str, enum.Enum):
    """Estados posibles de un curso."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Course(Base):
    """
    Curso o proyecto de aprendizaje.

    Atributos:
        id: UUID único del curso
        user_id: ID del usuario propietario
        title: Título del curso
        description: Descripción detallada
        status: Estado del curso (draft, active, completed, archived)
        course_metadata: Datos adicionales (tecnologías, recursos, etc.)
        progress_percentage: Progreso del curso (0-100)
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
        completed_at: Fecha de completado

    Relaciones:
        owner: Usuario propietario del curso
        goals: Goals asociados al curso
        embeddings: Embeddings de documentación del curso
    """

    __tablename__ = "courses"

    # Primary Key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Course Info
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Status
    status: Mapped[CourseStatus] = mapped_column(
        Enum(CourseStatus),
        default=CourseStatus.DRAFT,
        nullable=False,
        index=True
    )

    # Progress
    progress_percentage: Mapped[float] = mapped_column(default=0.0, nullable=False)

    # Course metadata (JSON)
    # Estructura: {
    #   "technologies": ["Python", "FastAPI", "React"],
    #   "resources": [{"type": "doc", "url": "..."}],
    #   "difficulty": "intermediate",
    #   "estimated_hours": 40
    # }
    course_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=True)

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
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="courses")

    goals: Mapped[List["Goal"]] = relationship(
        "Goal",
        back_populates="course",
        cascade="all, delete-orphan"
    )

    embeddings: Mapped[List["Embedding"]] = relationship(
        "Embedding",
        foreign_keys="[Embedding.entity_id]",
        primaryjoin="and_(Course.id == Embedding.entity_id, Embedding.entity_type == 'course')",
        viewonly=True
    )

    def __repr__(self) -> str:
        return f"<Course(id={self.id}, title={self.title}, status={self.status.value})>"
