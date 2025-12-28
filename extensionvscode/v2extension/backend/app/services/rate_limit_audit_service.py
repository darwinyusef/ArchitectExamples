"""
Rate Limit Audit Service - Tracking y auditoría de rate limits.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RateLimitAudit, RateLimitAction, RateLimitStatus
from app.core.rate_limiter import RateLimitResult


class RateLimitAuditService:
    """Servicio para auditar rate limits y detectar patrones sospechosos."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_request(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        action: RateLimitAction,
        rate_limit_result: RateLimitResult,
        response_time_ms: Optional[float] = None,
        http_status_code: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        openai_usage: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> RateLimitAudit:
        """
        Registrar un request en la auditoría.

        Args:
            user_id: ID del usuario
            endpoint: Endpoint llamado
            method: Método HTTP
            action: Tipo de acción
            rate_limit_result: Resultado del rate limiter
            response_time_ms: Tiempo de respuesta
            http_status_code: Código de status HTTP
            ip_address: IP del cliente
            user_agent: User agent del cliente
            openai_usage: Uso de tokens de OpenAI
            metadata: Metadata adicional

        Returns:
            RateLimitAudit creado
        """
        # Determinar status
        if rate_limit_result.allowed:
            status = RateLimitStatus.ALLOWED
        else:
            status = RateLimitStatus.RATE_LIMITED

        # Calcular costo estimado si hay uso de OpenAI
        estimated_cost_cents = None
        if openai_usage:
            estimated_cost_cents = self._calculate_cost(
                model=openai_usage.get("model", "text-embedding-3-small"),
                prompt_tokens=openai_usage.get("prompt_tokens", 0),
                completion_tokens=openai_usage.get("completion_tokens", 0)
            )

        # Detectar comportamiento sospechoso
        is_suspicious, alert_reason = await self._check_suspicious_activity(
            user_id=user_id,
            action=action,
            rate_limit_result=rate_limit_result,
            endpoint=endpoint
        )

        # Crear registro de auditoría
        audit = RateLimitAudit(
            id=str(uuid.uuid4()),
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            action=action,
            status=status,
            allowed=rate_limit_result.allowed,
            tokens_requested=rate_limit_result.tokens_requested,
            tokens_available=rate_limit_result.tokens_available,
            tokens_consumed=rate_limit_result.tokens_consumed,
            openai_prompt_tokens=openai_usage.get("prompt_tokens") if openai_usage else None,
            openai_completion_tokens=openai_usage.get("completion_tokens") if openai_usage else None,
            openai_total_tokens=openai_usage.get("total_tokens") if openai_usage else None,
            openai_model=openai_usage.get("model") if openai_usage else None,
            estimated_cost_cents=estimated_cost_cents,
            response_time_ms=response_time_ms,
            http_status_code=http_status_code,
            rate_limit_key=rate_limit_result.limit_key,
            rate_limit_window_seconds=rate_limit_result.window_seconds,
            rate_limit_max_requests=rate_limit_result.max_requests,
            current_request_count=rate_limit_result.current_count,
            is_suspicious=is_suspicious,
            alert_triggered=is_suspicious,
            alert_reason=alert_reason,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
            timestamp=datetime.utcnow()
        )

        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(audit)

        return audit

    async def get_user_statistics(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Obtener estadísticas de uso de un usuario.

        Args:
            user_id: ID del usuario
            start_date: Fecha inicio
            end_date: Fecha fin

        Returns:
            Dict con estadísticas
        """
        # Default: últimas 24 horas
        if not start_date:
            start_date = datetime.utcnow() - timedelta(hours=24)
        if not end_date:
            end_date = datetime.utcnow()

        query = select(RateLimitAudit).where(
            RateLimitAudit.user_id == user_id,
            RateLimitAudit.timestamp >= start_date,
            RateLimitAudit.timestamp <= end_date
        )

        result = await self.db.execute(query)
        audits = result.scalars().all()

        # Calcular estadísticas
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

        # Tokens OpenAI
        total_openai_tokens = sum(a.openai_total_tokens or 0 for a in audits)
        total_cost_cents = sum(a.estimated_cost_cents or 0 for a in audits)

        # Alertas
        total_alerts = sum(1 for a in audits if a.alert_triggered)

        # Tiempos de respuesta promedio
        response_times = [a.response_time_ms for a in audits if a.response_time_ms]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        return {
            "user_id": user_id,
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
            "by_action": by_action,
            "openai": {
                "total_tokens": total_openai_tokens,
                "estimated_cost_usd": total_cost_cents / 100 if total_cost_cents else 0
            },
            "alerts": {
                "total": total_alerts
            },
            "performance": {
                "avg_response_time_ms": avg_response_time
            }
        }

    async def get_suspicious_activities(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> list[RateLimitAudit]:
        """Obtener actividades sospechosas recientes."""
        since = datetime.utcnow() - timedelta(hours=hours)

        query = select(RateLimitAudit).where(
            RateLimitAudit.is_suspicious == True,
            RateLimitAudit.timestamp >= since
        ).order_by(RateLimitAudit.timestamp.desc()).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_top_consumers(
        self,
        action: Optional[RateLimitAction] = None,
        hours: int = 24,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """Obtener usuarios con mayor consumo."""
        since = datetime.utcnow() - timedelta(hours=hours)

        query = select(
            RateLimitAudit.user_id,
            func.count(RateLimitAudit.id).label('request_count'),
            func.sum(RateLimitAudit.openai_total_tokens).label('total_tokens'),
            func.sum(RateLimitAudit.estimated_cost_cents).label('total_cost')
        ).where(
            RateLimitAudit.timestamp >= since
        )

        if action:
            query = query.where(RateLimitAudit.action == action)

        query = query.group_by(RateLimitAudit.user_id).order_by(
            func.count(RateLimitAudit.id).desc()
        ).limit(limit)

        result = await self.db.execute(query)
        rows = result.all()

        return [
            {
                "user_id": row[0],
                "request_count": row[1],
                "total_tokens": row[2] or 0,
                "total_cost_usd": (row[3] or 0) / 100
            }
            for row in rows
        ]

    async def _check_suspicious_activity(
        self,
        user_id: str,
        action: RateLimitAction,
        rate_limit_result: RateLimitResult,
        endpoint: str
    ) -> tuple[bool, Optional[str]]:
        """
        Detectar actividad sospechosa.

        Returns:
            (is_suspicious, alert_reason)
        """
        # Obtener requests recientes (últimos 5 minutos)
        since = datetime.utcnow() - timedelta(minutes=5)
        query = select(func.count(RateLimitAudit.id)).where(
            RateLimitAudit.user_id == user_id,
            RateLimitAudit.action == action,
            RateLimitAudit.timestamp >= since
        )
        result = await self.db.execute(query)
        recent_count = result.scalar()

        # Umbral sospechoso: 5x el límite normal en 5 minutos
        threshold = rate_limit_result.max_requests * 5

        if recent_count and recent_count > threshold:
            return True, f"Excessive requests: {recent_count} in 5 minutes (threshold: {threshold})"

        # Verificar si está siendo bloqueado constantemente
        if not rate_limit_result.allowed:
            query = select(func.count(RateLimitAudit.id)).where(
                RateLimitAudit.user_id == user_id,
                RateLimitAudit.action == action,
                RateLimitAudit.allowed == False,
                RateLimitAudit.timestamp >= since
            )
            result = await self.db.execute(query)
            blocked_count = result.scalar()

            if blocked_count and blocked_count > 10:
                return True, f"Multiple rate limit violations: {blocked_count} blocked requests in 5 minutes"

        return False, None

    def _calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> float:
        """
        Calcular costo estimado en centavos de dólar.

        Precios (por 1M tokens):
        - text-embedding-3-small: $0.02 / 1M tokens
        - text-embedding-3-large: $0.13 / 1M tokens
        - gpt-3.5-turbo: $0.50 / 1M input, $1.50 / 1M output
        - gpt-4: $30 / 1M input, $60 / 1M output
        """
        costs = {
            "text-embedding-3-small": {"input": 0.02, "output": 0},
            "text-embedding-3-large": {"input": 0.13, "output": 0},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "gpt-4": {"input": 30.0, "output": 60.0},
            "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        }

        # Default costs si no se encuentra el modelo
        default_cost = {"input": 0.50, "output": 1.50}

        model_costs = costs.get(model, default_cost)

        # Calcular costo (convertir a centavos)
        input_cost = (prompt_tokens / 1_000_000) * model_costs["input"] * 100
        output_cost = (completion_tokens / 1_000_000) * model_costs["output"] * 100

        return input_cost + output_cost
