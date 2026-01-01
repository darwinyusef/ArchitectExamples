"""
CodeSnapshot model - Snapshots de código para validación y análisis.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, ForeignKey, Boolean, JSON, Float, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class CodeSnapshot(Base):
    """
    Snapshot de código enviado por el usuario para validación.

    Los snapshots se usan para:
    1. Validar código con agentes de IA
    2. Generar feedback contextual
    3. Detectar patrones y antipatrones
    4. Crear embeddings de código para RAG
    5. Mantener historial de cambios

    Atributos:
        id: UUID único del snapshot
        task_id: ID de la task asociada
        user_id: ID del usuario
        file_path: Path del archivo de código
        language: Lenguaje de programación
        code_content: Contenido del código
        validation_passed: Si pasó la validación
        validation_score: Score de validación (0-1)
        validation_feedback: Feedback generado por IA
        issues_found: Lista de issues encontrados
        snapshot_metadata: Metadatos adicionales
        storage_path: Path en S3/MinIO donde se guardó
        created_at: Timestamp de creación

    Relaciones:
        task: Task asociada
        user: Usuario propietario
        embeddings: Embeddings del código
    """

    __tablename__ = "code_snapshots"

    # Primary Key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Foreign Keys
    task_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Code Info
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Code Content (puede ser grande, considerar BLOB para archivos grandes)
    code_content: Mapped[str] = mapped_column(Text, nullable=False)

    # Validation Results
    validation_passed: Mapped[bool] = mapped_column(Boolean, nullable=True, index=True)
    validation_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # AI Feedback
    validation_feedback: Mapped[str] = mapped_column(Text, nullable=True)

    # Issues (JSON)
    # Estructura: [
    #   {
    #     "type": "error|warning|info",
    #     "line": 42,
    #     "column": 10,
    #     "message": "Variable not defined",
    #     "suggestion": "Import or define variable"
    #   }
    # ]
    issues_found: Mapped[list] = mapped_column(JSON, nullable=True)

    # Snapshot metadata (JSON)
    # Estructura: {
    #   "lines_of_code": 150,
    #   "complexity": "medium",
    #   "dependencies": ["fastapi", "sqlalchemy"],
    #   "tests_included": true,
    #   "test_coverage": 0.85,
    #   "git_commit": "abc123"
    # }
    snapshot_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=True)

    # Storage (path en S3/MinIO para archivos grandes)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Relationships
    task: Mapped[Optional["Task"]] = relationship("Task", back_populates="code_snapshots")

    user: Mapped["User"] = relationship("User", back_populates="code_snapshots")

    embeddings: Mapped[list["Embedding"]] = relationship(
        "Embedding",
        foreign_keys="[Embedding.entity_id]",
        primaryjoin="and_(CodeSnapshot.id == Embedding.entity_id, Embedding.entity_type == 'code_snapshot')",
        viewonly=True
    )

    # Indexes
    __table_args__ = (
        Index("idx_code_snapshots_task_created", "task_id", "created_at"),
        Index("idx_code_snapshots_user_lang", "user_id", "language", "created_at"),
        Index("idx_code_snapshots_validated", "validation_passed", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<CodeSnapshot(id={self.id}, file_path={self.file_path}, validated={self.validation_passed})>"
