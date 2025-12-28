"""
Admin Rate Limit Endpoints - Gestión y monitoreo de rate limits.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rate_limiter import get_rate_limiter
from app.services.rate_limit_audit_service import RateLimitAuditService
from app.models import RateLimitAction

router = APIRouter()


# ============================================================================
# GET /admin/rate-limits/users/{user_id}/status
# ============================================================================

@router.get("/users/{user_id}/status")
async def get_user_rate_limit_status(
    user_id: str,
    # TODO: Add admin authentication
    # current_user: User = Depends(require_admin)
):
    """
    Obtener estado actual de todos los rate limits de un usuario.

    Muestra cuántos tokens tiene disponibles en cada categoría.

    **Returns:**
    ```json
    {
        "user_id": "usr_123",
        "timestamp": "2025-01-15T10:30:00",
        "limits": {
            "api_call": {
                "available_tokens": 85,
                "max_capacity": 150,
                "refill_rate": 1.67,
                "current_count": 15,
                "max_requests": 100,
                "window_seconds": 60
            },
            "embedding_generation": {...}
        }
    }
    ```
    """
    rate_limiter = await get_rate_limiter()
    status = await rate_limiter.get_user_status(user_id)

    return {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "limits": status
    }


# ============================================================================
# GET /admin/rate-limits/audits
# ============================================================================

@router.get("/audits")
async def get_rate_limit_audits(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    action: Optional[RateLimitAction] = Query(None, description="Filter by action type"),
    start_date: Optional[datetime] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date (ISO format)"),
    only_blocked: bool = Query(False, description="Only show blocked requests"),
    only_suspicious: bool = Query(False, description="Only show suspicious activity"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener logs de auditoría de rate limits.

    Permite filtrar por usuario, acción, fechas, etc.

    **Example:**
    ```
    GET /admin/rate-limits/audits?user_id=usr_123&only_blocked=true&limit=50
    ```
    """
    from sqlalchemy import select
    from app.models import RateLimitAudit

    # Build query
    query = select(RateLimitAudit)

    if user_id:
        query = query.where(RateLimitAudit.user_id == user_id)

    if action:
        query = query.where(RateLimitAudit.action == action)

    if start_date:
        query = query.where(RateLimitAudit.timestamp >= start_date)

    if end_date:
        query = query.where(RateLimitAudit.timestamp <= end_date)

    if only_blocked:
        query = query.where(RateLimitAudit.allowed == False)

    if only_suspicious:
        query = query.where(RateLimitAudit.is_suspicious == True)

    query = query.order_by(RateLimitAudit.timestamp.desc()).limit(limit)

    result = await db.execute(query)
    audits = result.scalars().all()

    return {
        "total": len(audits),
        "filters": {
            "user_id": user_id,
            "action": action.value if action else None,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "only_blocked": only_blocked,
            "only_suspicious": only_suspicious
        },
        "audits": [
            {
                "id": audit.id,
                "user_id": audit.user_id,
                "endpoint": audit.endpoint,
                "method": audit.method,
                "action": audit.action.value,
                "status": audit.status.value,
                "allowed": audit.allowed,
                "tokens_requested": audit.tokens_requested,
                "tokens_available": audit.tokens_available,
                "tokens_consumed": audit.tokens_consumed,
                "openai_tokens": {
                    "prompt": audit.openai_prompt_tokens,
                    "completion": audit.openai_completion_tokens,
                    "total": audit.openai_total_tokens,
                    "model": audit.openai_model
                } if audit.openai_total_tokens else None,
                "estimated_cost_usd": (audit.estimated_cost_cents / 100) if audit.estimated_cost_cents else None,
                "response_time_ms": audit.response_time_ms,
                "http_status_code": audit.http_status_code,
                "is_suspicious": audit.is_suspicious,
                "alert_reason": audit.alert_reason,
                "ip_address": audit.ip_address,
                "timestamp": audit.timestamp.isoformat()
            }
            for audit in audits
        ]
    }


# ============================================================================
# GET /admin/rate-limits/statistics
# ============================================================================

@router.get("/statistics")
async def get_rate_limit_statistics(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener estadísticas de uso de rate limits.

    Si se provee user_id, retorna estadísticas del usuario.
    Si no, retorna estadísticas globales del sistema.

    **User Statistics Example:**
    ```json
    {
        "user_id": "usr_123",
        "period": {
            "start": "2025-01-15T00:00:00",
            "end": "2025-01-16T00:00:00"
        },
        "requests": {
            "total": 450,
            "allowed": 420,
            "blocked": 30,
            "block_rate": 0.067
        },
        "by_action": {
            "embedding_generation": {
                "total": 180,
                "allowed": 170,
                "blocked": 10
            }
        },
        "openai": {
            "total_tokens": 125000,
            "estimated_cost_usd": 2.50
        }
    }
    ```
    """
    audit_service = RateLimitAuditService(db)

    if user_id:
        # User statistics
        stats = await audit_service.get_user_statistics(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        return stats
    else:
        # Global statistics
        # Default: últimas 24 horas
        if not start_date:
            start_date = datetime.utcnow() - timedelta(hours=24)
        if not end_date:
            end_date = datetime.utcnow()

        from sqlalchemy import select, func
        from app.models import RateLimitAudit

        query = select(RateLimitAudit).where(
            RateLimitAudit.timestamp >= start_date,
            RateLimitAudit.timestamp <= end_date
        )

        result = await db.execute(query)
        audits = result.scalars().all()

        total_requests = len(audits)
        allowed_requests = sum(1 for a in audits if a.allowed)
        blocked_requests = total_requests - allowed_requests

        # Por acción
        by_action = {}
        for action in RateLimitAction:
            action_audits = [a for a in audits if a.action == action]
            if action_audits:
                by_action[action.value] = {
                    "total": len(action_audits),
                    "allowed": sum(1 for a in action_audits if a.allowed),
                    "blocked": sum(1 for a in action_audits if not a.allowed)
                }

        # Tokens y costos totales
        total_openai_tokens = sum(a.openai_total_tokens or 0 for a in audits)
        total_cost_cents = sum(a.estimated_cost_cents or 0 for a in audits)

        # Usuarios únicos
        unique_users = len(set(a.user_id for a in audits))

        # Alertas
        total_alerts = sum(1 for a in audits if a.alert_triggered)

        return {
            "system": "global",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "requests": {
                "total": total_requests,
                "allowed": allowed_requests,
                "blocked": blocked_requests,
                "block_rate": blocked_requests / total_requests if total_requests > 0 else 0
            },
            "users": {
                "unique_users": unique_users,
                "avg_requests_per_user": total_requests / unique_users if unique_users > 0 else 0
            },
            "by_action": by_action,
            "openai": {
                "total_tokens": total_openai_tokens,
                "estimated_cost_usd": total_cost_cents / 100 if total_cost_cents else 0
            },
            "alerts": {
                "total": total_alerts,
                "rate": total_alerts / total_requests if total_requests > 0 else 0
            }
        }


# ============================================================================
# POST /admin/rate-limits/users/{user_id}/reset
# ============================================================================

@router.post("/users/{user_id}/reset")
async def reset_user_rate_limits(
    user_id: str,
    action: Optional[RateLimitAction] = Query(None, description="Specific action to reset (or all if not provided)"),
    # TODO: Add admin authentication
    # current_user: User = Depends(require_admin)
):
    """
    Resetear rate limits de un usuario.

    Útil para casos de soporte o testing.

    **Examples:**
    ```
    POST /admin/rate-limits/users/usr_123/reset
    # Resetea todos los rate limits

    POST /admin/rate-limits/users/usr_123/reset?action=embedding_generation
    # Solo resetea embedding_generation
    ```

    **Security:** Requiere autenticación de administrador.
    """
    rate_limiter = await get_rate_limiter()

    if action:
        await rate_limiter.reset_user_limits(user_id, action.value)
        message = f"Reset rate limit for action '{action.value}'"
    else:
        await rate_limiter.reset_user_limits(user_id)
        message = "Reset all rate limits"

    return {
        "success": True,
        "user_id": user_id,
        "action": action.value if action else "all",
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# GET /admin/rate-limits/top-consumers
# ============================================================================

@router.get("/top-consumers")
async def get_top_consumers(
    action: Optional[RateLimitAction] = Query(None, description="Filter by action type"),
    hours: int = Query(24, ge=1, le=720, description="Time window in hours"),
    limit: int = Query(10, ge=1, le=100, description="Max results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener usuarios con mayor consumo de rate limits.

    Útil para identificar usuarios power o detectar abuso.

    **Response Example:**
    ```json
    {
        "period_hours": 24,
        "action": "embedding_generation",
        "top_consumers": [
            {
                "user_id": "usr_456",
                "request_count": 1850,
                "total_tokens": 450000,
                "total_cost_usd": 9.00
            },
            {
                "user_id": "usr_123",
                "request_count": 920,
                "total_tokens": 180000,
                "total_cost_usd": 3.60
            }
        ]
    }
    ```
    """
    audit_service = RateLimitAuditService(db)

    top_consumers = await audit_service.get_top_consumers(
        action=action,
        hours=hours,
        limit=limit
    )

    return {
        "period_hours": hours,
        "action": action.value if action else "all",
        "limit": limit,
        "top_consumers": top_consumers
    }


# ============================================================================
# GET /admin/rate-limits/suspicious
# ============================================================================

@router.get("/suspicious")
async def get_suspicious_activities(
    hours: int = Query(24, ge=1, le=720, description="Time window in hours"),
    limit: int = Query(100, ge=1, le=1000, description="Max results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener actividades sospechosas detectadas.

    Retorna requests que fueron flagueados como sospechosos por:
    - Exceder 5x el rate limit normal en 5 minutos
    - Múltiples requests bloqueados consecutivos (>10 en 5 min)

    **Response Example:**
    ```json
    {
        "period_hours": 24,
        "total_suspicious": 5,
        "activities": [
            {
                "id": "audit_789",
                "user_id": "usr_suspicious",
                "endpoint": "/api/v1/goals",
                "action": "embedding_generation",
                "alert_reason": "Excessive requests: 150 in 5 minutes (threshold: 100)",
                "timestamp": "2025-01-15T14:23:00",
                "ip_address": "192.168.1.100",
                "request_count_recent": 150
            }
        ]
    }
    ```
    """
    audit_service = RateLimitAuditService(db)

    suspicious = await audit_service.get_suspicious_activities(
        hours=hours,
        limit=limit
    )

    return {
        "period_hours": hours,
        "total_suspicious": len(suspicious),
        "activities": [
            {
                "id": audit.id,
                "user_id": audit.user_id,
                "endpoint": audit.endpoint,
                "method": audit.method,
                "action": audit.action.value,
                "alert_reason": audit.alert_reason,
                "timestamp": audit.timestamp.isoformat(),
                "ip_address": audit.ip_address,
                "user_agent": audit.user_agent,
                "metadata": audit.metadata
            }
            for audit in suspicious
        ]
    }


# ============================================================================
# GET /admin/rate-limits/config
# ============================================================================

@router.get("/config")
async def get_rate_limit_config():
    """
    Obtener configuración actual de rate limits.

    Muestra los límites configurados para cada tipo de acción.

    **Response Example:**
    ```json
    {
        "configs": {
            "api_call": {
                "max_requests": 100,
                "window_seconds": 60,
                "burst_multiplier": 1.5,
                "effective_burst_limit": 150
            },
            "embedding_generation": {
                "max_requests": 20,
                "window_seconds": 60,
                "burst_multiplier": 1.2,
                "effective_burst_limit": 24
            }
        }
    }
    ```
    """
    rate_limiter = await get_rate_limiter()

    configs = {}
    for action, config in rate_limiter.configs.items():
        configs[action] = {
            "max_requests": config.max_requests,
            "window_seconds": config.window_seconds,
            "burst_multiplier": config.burst_multiplier,
            "effective_burst_limit": int(config.max_requests * config.burst_multiplier),
            "description": _get_action_description(action)
        }

    return {
        "configs": configs,
        "algorithm": "Token Bucket",
        "backend": "Redis"
    }


def _get_action_description(action: str) -> str:
    """Helper para describir cada acción."""
    descriptions = {
        "api_call": "General API calls",
        "embedding_generation": "OpenAI embedding generation",
        "chat_completion": "OpenAI chat completions",
        "code_validation": "Code validation requests",
        "rag_search": "RAG semantic search queries",
        "bulk_create": "Bulk creation operations",
        "bulk_update": "Bulk update operations"
    }
    return descriptions.get(action, "Unknown action")
