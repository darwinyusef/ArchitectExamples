"""
User model - Representa usuarios del sistema.
"""

from datetime import datetime
from typing import List
from sqlalchemy import String, DateTime, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class User(Base):
    """
    Usuario del sistema.

    Atributos:
        id: UUID único del usuario
        email: Email único del usuario
        username: Nombre de usuario único
        hashed_password: Password hasheada con bcrypt
        full_name: Nombre completo del usuario
        is_active: Si el usuario está activo
        is_superuser: Si el usuario es administrador
        user_metadata: Datos adicionales (preferencias, configuración)
        created_at: Fecha de creación
        updated_at: Fecha de última actualización
        last_login_at: Fecha de último login

    Relaciones:
        courses: Cursos creados por el usuario
        goals: Goals creados por el usuario
        tasks: Tasks asignadas al usuario
        events: Eventos generados por el usuario
        embeddings: Embeddings generados por el usuario
        code_snapshots: Snapshots de código del usuario
    """

    __tablename__ = "users"

    # Primary Key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Authentication
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # User metadata (JSON)
    # Estructura: {
    #   "preferences": {"theme": "dark", "language": "es"},
    #   "settings": {"notifications": true},
    #   "profile": {"avatar_url": "...", "bio": "..."}
    # }
    user_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=True)

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
    last_login_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships
    courses: Mapped[List["Course"]] = relationship(
        "Course",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    goals: Mapped[List["Goal"]] = relationship(
        "Goal",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="assigned_to",
        cascade="all, delete-orphan"
    )

    events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    embeddings: Mapped[List["Embedding"]] = relationship(
        "Embedding",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    code_snapshots: Mapped[List["CodeSnapshot"]] = relationship(
        "CodeSnapshot",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
