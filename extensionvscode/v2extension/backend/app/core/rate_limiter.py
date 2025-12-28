"""
Rate Limiter con Token Bucket Algorithm.

Implementa rate limiting usando Redis para almacenar los buckets.
"""

import time
from typing import Tuple, Optional
from dataclasses import dataclass
import redis.asyncio as redis

from app.core.config import settings


@dataclass
class RateLimitConfig:
    """Configuración de rate limit."""

    max_requests: int  # Máximo de requests permitidos
    window_seconds: int  # Ventana de tiempo en segundos
    burst_multiplier: float = 1.5  # Permite burst hasta 1.5x el límite


@dataclass
class RateLimitResult:
    """Resultado de verificación de rate limit."""

    allowed: bool
    tokens_available: int
    tokens_requested: int
    tokens_consumed: int
    retry_after_seconds: Optional[float] = None
    limit_key: str = ""
    window_seconds: int = 0
    max_requests: int = 0
    current_count: int = 0


class TokenBucket:
    """
    Token Bucket Algorithm implementation.

    Características:
    - Tokens se regeneran a tasa constante
    - Permite bursts hasta burst_multiplier * max_requests
    - Usa Redis para persistencia distribuida
    - Atomic operations para concurrencia
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def consume(
        self,
        key: str,
        tokens: int,
        config: RateLimitConfig
    ) -> RateLimitResult:
        """
        Intenta consumir tokens del bucket.

        Args:
            key: Identificador único del bucket (ej: "user:123:embedding")
            tokens: Número de tokens a consumir
            config: Configuración del rate limit

        Returns:
            RateLimitResult con el resultado de la operación
        """
        now = time.time()

        # Capacidad máxima del bucket (permite bursts)
        max_capacity = int(config.max_requests * config.burst_multiplier)

        # Tasa de regeneración (tokens por segundo)
        refill_rate = config.max_requests / config.window_seconds

        # Usar Lua script para operación atómica
        lua_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local tokens_to_consume = tonumber(ARGV[2])
        local max_capacity = tonumber(ARGV[3])
        local refill_rate = tonumber(ARGV[4])
        local ttl = tonumber(ARGV[5])

        -- Obtener estado actual del bucket
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local current_tokens = tonumber(bucket[1]) or max_capacity
        local last_refill = tonumber(bucket[2]) or now

        -- Calcular tokens a añadir basado en tiempo transcurrido
        local time_passed = now - last_refill
        local tokens_to_add = time_passed * refill_rate
        current_tokens = math.min(max_capacity, current_tokens + tokens_to_add)

        -- Intentar consumir tokens
        if current_tokens >= tokens_to_consume then
            -- Éxito: consumir tokens
            current_tokens = current_tokens - tokens_to_consume

            -- Actualizar bucket
            redis.call('HMSET', key,
                'tokens', current_tokens,
                'last_refill', now
            )
            redis.call('EXPIRE', key, ttl)

            return {1, current_tokens, tokens_to_consume}
        else
            -- Fallo: no hay suficientes tokens
            -- Calcular tiempo hasta que haya suficientes tokens
            local tokens_needed = tokens_to_consume - current_tokens
            local retry_after = tokens_needed / refill_rate

            return {0, current_tokens, 0, retry_after}
        end
        """

        try:
            result = await self.redis.eval(
                lua_script,
                1,  # number of keys
                key,  # KEYS[1]
                now,  # ARGV[1]
                tokens,  # ARGV[2]
                max_capacity,  # ARGV[3]
                refill_rate,  # ARGV[4]
                config.window_seconds * 2  # ARGV[5] - TTL
            )

            allowed = bool(result[0])
            tokens_available = int(result[1])
            tokens_consumed = int(result[2]) if allowed else 0
            retry_after = float(result[3]) if len(result) > 3 else None

            # Obtener count actual para auditoría
            count_key = f"{key}:count"
            if allowed:
                current_count = await self.redis.incr(count_key)
                await self.redis.expire(count_key, config.window_seconds)
            else:
                current_count = await self.redis.get(count_key) or 0
                current_count = int(current_count)

            return RateLimitResult(
                allowed=allowed,
                tokens_available=tokens_available,
                tokens_requested=tokens,
                tokens_consumed=tokens_consumed,
                retry_after_seconds=retry_after,
                limit_key=key,
                window_seconds=config.window_seconds,
                max_requests=config.max_requests,
                current_count=current_count
            )

        except Exception as e:
            # En caso de error con Redis, permitir el request (fail-open)
            # pero loggear el error
            print(f"Rate limiter error: {e}")
            return RateLimitResult(
                allowed=True,
                tokens_available=config.max_requests,
                tokens_requested=tokens,
                tokens_consumed=0,
                limit_key=key,
                window_seconds=config.window_seconds,
                max_requests=config.max_requests,
                current_count=0
            )

    async def reset(self, key: str) -> None:
        """Reset un bucket (útil para testing)."""
        await self.redis.delete(key)
        await self.redis.delete(f"{key}:count")

    async def get_status(self, key: str, config: RateLimitConfig) -> dict:
        """Obtener status actual de un bucket."""
        now = time.time()
        max_capacity = int(config.max_requests * config.burst_multiplier)
        refill_rate = config.max_requests / config.window_seconds

        bucket = await self.redis.hmget(key, 'tokens', 'last_refill')
        current_tokens = float(bucket[0]) if bucket[0] else max_capacity
        last_refill = float(bucket[1]) if bucket[1] else now

        # Calcular tokens disponibles ahora
        time_passed = now - last_refill
        tokens_to_add = time_passed * refill_rate
        available_tokens = min(max_capacity, current_tokens + tokens_to_add)

        count_key = f"{key}:count"
        current_count = await self.redis.get(count_key) or 0

        return {
            "available_tokens": available_tokens,
            "max_capacity": max_capacity,
            "refill_rate": refill_rate,
            "current_count": int(current_count),
            "max_requests": config.max_requests,
            "window_seconds": config.window_seconds
        }


class RateLimiter:
    """
    Rate Limiter principal con configuraciones predefinidas.
    """

    def __init__(self, redis_client: redis.Redis):
        self.bucket = TokenBucket(redis_client)

        # Configuraciones predefinidas
        self.configs = {
            # API endpoints normales
            "api_call": RateLimitConfig(
                max_requests=100,  # 100 requests
                window_seconds=60,  # por minuto
                burst_multiplier=1.5
            ),

            # OpenAI embeddings (más restrictivo)
            "embedding_generation": RateLimitConfig(
                max_requests=20,  # 20 embeddings
                window_seconds=60,  # por minuto
                burst_multiplier=1.2
            ),

            # OpenAI chat completions (muy restrictivo)
            "chat_completion": RateLimitConfig(
                max_requests=10,  # 10 completions
                window_seconds=60,  # por minuto
                burst_multiplier=1.0  # Sin burst
            ),

            # Validación de código
            "code_validation": RateLimitConfig(
                max_requests=30,  # 30 validaciones
                window_seconds=60,  # por minuto
                burst_multiplier=1.3
            ),

            # RAG searches
            "rag_search": RateLimitConfig(
                max_requests=50,  # 50 búsquedas
                window_seconds=60,  # por minuto
                burst_multiplier=1.5
            ),

            # Operaciones bulk (muy restrictivo)
            "bulk_create": RateLimitConfig(
                max_requests=5,  # 5 operaciones bulk
                window_seconds=60,  # por minuto
                burst_multiplier=1.0
            ),
        }

    def get_key(self, user_id: str, action: str) -> str:
        """Generar key de Redis para rate limit."""
        return f"rate_limit:{user_id}:{action}"

    async def check_limit(
        self,
        user_id: str,
        action: str,
        tokens: int = 1,
        custom_config: Optional[RateLimitConfig] = None
    ) -> RateLimitResult:
        """
        Verificar y consumir rate limit.

        Args:
            user_id: ID del usuario
            action: Tipo de acción (debe estar en self.configs)
            tokens: Número de tokens a consumir
            custom_config: Configuración custom (opcional)

        Returns:
            RateLimitResult
        """
        config = custom_config or self.configs.get(action)
        if not config:
            # Si no hay config, usar default
            config = self.configs["api_call"]

        key = self.get_key(user_id, action)
        return await self.bucket.consume(key, tokens, config)

    async def reset_user_limits(self, user_id: str, action: Optional[str] = None) -> None:
        """Reset limits para un usuario (útil para testing o admin)."""
        if action:
            key = self.get_key(user_id, action)
            await self.bucket.reset(key)
        else:
            # Reset all actions
            for action in self.configs.keys():
                key = self.get_key(user_id, action)
                await self.bucket.reset(key)

    async def get_user_status(self, user_id: str) -> dict:
        """Obtener status de todos los rate limits de un usuario."""
        status = {}
        for action, config in self.configs.items():
            key = self.get_key(user_id, action)
            status[action] = await self.bucket.get_status(key, config)
        return status


# Singleton instance
_rate_limiter: Optional[RateLimiter] = None


async def get_rate_limiter() -> RateLimiter:
    """Obtener instancia del rate limiter."""
    global _rate_limiter

    if _rate_limiter is None:
        # Crear conexión a Redis
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        _rate_limiter = RateLimiter(redis_client)

    return _rate_limiter
