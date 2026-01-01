"""
Embedding model - Vector embeddings para RAG (Retrieval-Augmented Generation).
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class Embedding(Base):
    """
    Vector Embeddings para RAG.

    Los embeddings permiten búsqueda semántica y recuperación de contexto
    para los agentes de LangGraph.

    Usos:
    1. Recuperar goals/tasks similares
    2. Buscar documentación relevante de cursos
    3. Encontrar código similar ya validado
    4. Contextualizar feedback de IA

    Atributos:
        id: UUID único del embedding
        user_id: ID del usuario propietario
        entity_type: Tipo de entidad (goal, task, course, code)
        entity_id: ID de la entidad
        content: Texto original que se embeddeó
        embedding: Vector de 1536 dimensiones (OpenAI text-embedding-3-small)
        model: Modelo usado para generar el embedding
        embedding_metadata: Metadatos adicionales
        created_at: Timestamp de creación

    Relaciones:
        user: Usuario propietario

    Indexes:
        - HNSW index para búsqueda de vectores similares
        - Index compuesto para entity_type + entity_id
    """

    __tablename__ = "embeddings"

    # Primary Key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Entity Info (polymorphic)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Vector Embedding (1536 dimensiones para OpenAI text-embedding-3-small)
    # Puede ser 3072 para text-embedding-3-large
    embedding: Mapped[Vector] = mapped_column(Vector(1536), nullable=False)

    # Model Info
    model: Mapped[str] = mapped_column(
        String(100),
        default="text-embedding-3-small",
        nullable=False
    )

    # Embedding metadata (JSON)
    # Estructura: {
    #   "chunk_index": 0,
    #   "total_chunks": 1,
    #   "language": "en",
    #   "source": "user_input",
    #   "version": "1.0"
    # }
    embedding_metadata: Mapped[dict] = mapped_column("metadata", JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="embeddings")

    # Indexes
    __table_args__ = (
        # Index compuesto para buscar embeddings por entidad
        Index("idx_embeddings_entity", "entity_type", "entity_id"),

        # HNSW index para búsqueda de vectores similares (más rápido que IVFFlat)
        # Se crea con: CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops);
        # Esto se hace en las migraciones de Alembic
    )

    def __repr__(self) -> str:
        return f"<Embedding(id={self.id}, entity_type={self.entity_type}, entity_id={self.entity_id})>"


# Queries comunes para RAG:
#
# 1. Buscar goals similares (para sugerir contexto a agentes):
"""
SELECT g.*, e.content,
       1 - (e.embedding <=> :query_embedding) as similarity
FROM embeddings e
JOIN goals g ON e.entity_id = g.id
WHERE e.entity_type = 'goal'
  AND e.user_id = :user_id
ORDER BY e.embedding <=> :query_embedding
LIMIT 5;
"""

# 2. Buscar documentación de curso relevante:
"""
SELECT c.*, e.content,
       1 - (e.embedding <=> :query_embedding) as similarity
FROM embeddings e
JOIN courses c ON e.entity_id = c.id
WHERE e.entity_type = 'course'
  AND e.user_id = :user_id
ORDER BY e.embedding <=> :query_embedding
LIMIT 3;
"""

# 3. Buscar código similar ya validado:
"""
SELECT cs.*, e.content,
       1 - (e.embedding <=> :query_embedding) as similarity
FROM embeddings e
JOIN code_snapshots cs ON e.entity_id = cs.id
WHERE e.entity_type = 'code_snapshot'
  AND e.user_id = :user_id
  AND cs.validation_passed = true
ORDER BY e.embedding <=> :query_embedding
LIMIT 5;
"""
