"""
Rate Limit Audit Model - Tracking de rate limits y consumo de tokens.
"""

from datetime import datetime
from typing import Optional, Dict, Any
import enum

from sqlalchemy import String, Integer, Float, Boolean, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RateLimitAction(str, enum.Enum):
    """Tipos de acciones que consumen rate limit."""

    # API Calls
    API_CALL = "api_call"

    # OpenAI Operations
    EMBEDDING_GENERATION = "embedding_generation"
    CHAT_COMPLETION = "chat_completion"
    CODE_VALIDATION = "code_validation"

    # RAG Operations
    RAG_SEARCH = "rag_search"
    SIMILARITY_SEARCH = "similarity_search"

    # Bulk Operations
    BULK_CREATE = "bulk_create"
    BULK_UPDATE = "bulk_update"


class RateLimitStatus(str, enum.Enum):
    """Estado del rate limit."""

    ALLOWED = "allowed"
    RATE_LIMITED = "rate_limited"
    TOKEN_LIMIT_EXCEEDED = "token_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"


class RateLimitAudit(Base):
    """
    Auditoría de Rate Limits y consumo de tokens.

    Registra:
    - Cada request que consume recursos
    - Tokens de OpenAI consumidos
    - Rate limits alcanzados
    - Alertas de consumo excesivo
    """

    __tablename__ = "rate_limit_audits"

    # Primary key
    id: Mapped[str] = mapped_column(String(36), primary_key=True)

    # User tracking
    user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)

    # Request info
    endpoint: Mapped[str] = mapped_column(String(200), nullable=False)
    method: Mapped[str] = mapped_column(String(10), nullable=False)  # GET, POST, etc.
    action: Mapped[RateLimitAction] = mapped_column(
        SQLEnum(RateLimitAction),
        nullable=False,
        index=True
    )

    # Rate limit status
    status: Mapped[RateLimitStatus] = mapped_column(
        SQLEnum(RateLimitStatus),
        nullable=False,
        index=True
    )
    allowed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Token Bucket info
    tokens_requested: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    tokens_available: Mapped[int] = mapped_column(Integer, nullable=False)
    tokens_consumed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # OpenAI token tracking
    openai_prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    openai_completion_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    openai_total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    openai_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Cost tracking (in USD cents)
    estimated_cost_cents: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Response info
    response_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    http_status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Rate limit details
    rate_limit_key: Mapped[str] = mapped_column(String(200), nullable=False)
    rate_limit_window_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    rate_limit_max_requests: Mapped[int] = mapped_column(Integer, nullable=False)
    current_request_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Alert flags
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    alert_triggered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    alert_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # IP and user agent
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Additional metadata
    audit_metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)

    # Timestamps
    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    def __repr__(self) -> str:
        return (
            f"<RateLimitAudit(id={self.id}, user_id={self.user_id}, "
            f"action={self.action.value}, status={self.status.value}, "
            f"allowed={self.allowed})>"
        )
