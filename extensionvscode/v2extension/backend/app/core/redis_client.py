"""Redis client for caching and state management."""

import json
from typing import Any, Optional
import redis.asyncio as redis

from app.core.config import settings

# Global Redis client
_redis_client: Optional[redis.Redis] = None


async def init_redis() -> None:
    """Initialize Redis connection pool."""
    global _redis_client
    _redis_client = await redis.from_url(
        settings.REDIS_URL,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        encoding="utf-8",
        decode_responses=True,
    )


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


def get_redis() -> redis.Redis:
    """Get Redis client instance."""
    if _redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return _redis_client


class RedisService:
    """High-level Redis operations for common use cases."""

    def __init__(self) -> None:
        self.client = get_redis()

    # ==================== User Sessions ====================

    async def set_user_session(self, user_id: str, session_data: dict[str, Any]) -> None:
        """Store user session data."""
        key = f"user_session:{user_id}"
        await self.client.setex(
            key,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            json.dumps(session_data)
        )

    async def get_user_session(self, user_id: str) -> Optional[dict[str, Any]]:
        """Retrieve user session data."""
        key = f"user_session:{user_id}"
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def delete_user_session(self, user_id: str) -> None:
        """Delete user session."""
        key = f"user_session:{user_id}"
        await self.client.delete(key)

    # ==================== WebSocket Connections ====================

    async def add_ws_connection(self, connection_id: str, user_id: str) -> None:
        """Register a WebSocket connection."""
        key = f"ws_connections:{connection_id}"
        data = {
            "user_id": user_id,
            "connected_at": str(redis.asyncio.client.datetime.datetime.now()),
        }
        await self.client.setex(key, 3600, json.dumps(data))  # 1 hour TTL

    async def get_ws_connection(self, connection_id: str) -> Optional[dict[str, Any]]:
        """Get WebSocket connection info."""
        key = f"ws_connections:{connection_id}"
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def remove_ws_connection(self, connection_id: str) -> None:
        """Remove WebSocket connection."""
        key = f"ws_connections:{connection_id}"
        await self.client.delete(key)

    async def get_user_connections(self, user_id: str) -> list[str]:
        """Get all active connections for a user."""
        pattern = "ws_connections:*"
        connection_ids = []

        async for key in self.client.scan_iter(match=pattern):
            data = await self.client.get(key)
            if data:
                conn_data = json.loads(data)
                if conn_data.get("user_id") == user_id:
                    connection_ids.append(key.split(":")[1])

        return connection_ids

    # ==================== LangGraph State ====================

    async def set_goal_state(
        self,
        execution_id: str,
        state_data: dict[str, Any],
        ttl: int = 3600
    ) -> None:
        """Store LangGraph goal execution state."""
        key = f"goal_state:{execution_id}"
        await self.client.setex(key, ttl, json.dumps(state_data))

    async def get_goal_state(self, execution_id: str) -> Optional[dict[str, Any]]:
        """Retrieve LangGraph goal state."""
        key = f"goal_state:{execution_id}"
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def delete_goal_state(self, execution_id: str) -> None:
        """Delete goal state."""
        key = f"goal_state:{execution_id}"
        await self.client.delete(key)

    # ==================== Token Blacklist ====================

    async def blacklist_token(self, token: str, expires_in: int) -> None:
        """Add token to blacklist (for logout/revocation)."""
        key = f"blacklist:{token}"
        await self.client.setex(key, expires_in, "1")

    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        key = f"blacklist:{token}"
        return await self.client.exists(key) > 0

    # ==================== Rate Limiting ====================

    async def check_rate_limit(self, user_id: str, limit: int, window: int) -> bool:
        """
        Check if user is within rate limit.

        Args:
            user_id: User identifier
            limit: Max requests allowed
            window: Time window in seconds

        Returns:
            True if within limit, False otherwise
        """
        key = f"rate_limit:{user_id}"
        current = await self.client.incr(key)

        if current == 1:
            await self.client.expire(key, window)

        return current <= limit
