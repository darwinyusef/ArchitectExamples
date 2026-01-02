"""WebSocket connection manager and message handler."""

import json
import logging
import uuid
from typing import Dict, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect, status
from datetime import datetime

from app.core.redis_client import RedisService
from app.core.security import decode_token

logger = logging.getLogger(__name__)


class WebSocketMessage:
    """WebSocket message structure."""

    def __init__(
        self,
        type: str,
        payload: dict[str, Any],
        correlation_id: Optional[str] = None
    ):
        self.type = type
        self.payload = payload
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, data: str) -> "WebSocketMessage":
        """Create from JSON string."""
        parsed = json.loads(data)
        return cls(
            type=parsed["type"],
            payload=parsed["payload"],
            correlation_id=parsed.get("correlation_id"),
        )


class ConnectionManager:
    """Manage WebSocket connections with authentication and user tracking."""

    def __init__(self) -> None:
        # Active connections: connection_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

        # User to connections mapping: user_id -> set of connection_ids
        self.user_connections: Dict[str, set[str]] = {}

        # Connection metadata: connection_id -> user_id
        self.connection_users: Dict[str, str] = {}

        # Redis service for persistence (lazy initialization)
        self._redis: Optional[RedisService] = None

    @property
    def redis(self) -> RedisService:
        """Get Redis service instance (lazy initialization)."""
        if self._redis is None:
            self._redis = RedisService()
        return self._redis

    async def authenticate(self, websocket: WebSocket) -> Optional[str]:
        """
        Authenticate WebSocket connection via JWT token.

        Args:
            websocket: WebSocket connection

        Returns:
            User ID if authenticated, None otherwise
        """
        # Extract token from query params or headers
        token = websocket.query_params.get("token")

        if not token:
            # Try to get from headers
            token = websocket.headers.get("Authorization", "").replace("Bearer ", "")

        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None

        # Check if token is blacklisted
        if await self.redis.is_token_blacklisted(token):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None

        # Decode and verify token
        payload = decode_token(token)
        if not payload:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None

        # Extract user ID
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None

        # Check token type (must be access token)
        if payload.get("type") != "access":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return None

        return user_id

    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """
        Register a new WebSocket connection.

        Args:
            websocket: WebSocket connection
            user_id: Authenticated user ID

        Returns:
            Connection ID
        """
        await websocket.accept()

        # Generate unique connection ID
        connection_id = str(uuid.uuid4())

        # Store connection
        self.active_connections[connection_id] = websocket
        self.connection_users[connection_id] = user_id

        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)

        # Store in Redis for cross-instance tracking
        await self.redis.add_ws_connection(connection_id, user_id)

        logger.info(f"User {user_id} connected (connection: {connection_id})")

        return connection_id

    async def disconnect(self, connection_id: str) -> None:
        """
        Remove a WebSocket connection.

        Args:
            connection_id: Connection identifier
        """
        # Get user ID
        user_id = self.connection_users.get(connection_id)

        # Remove from tracking
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]

        if connection_id in self.connection_users:
            del self.connection_users[connection_id]

        # Remove from user connections
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Remove from Redis
        await self.redis.remove_ws_connection(connection_id)

        logger.info(f"Connection {connection_id} disconnected")

    async def send_personal_message(
        self,
        message: WebSocketMessage,
        connection_id: str
    ) -> None:
        """
        Send a message to a specific connection.

        Args:
            message: Message to send
            connection_id: Target connection ID
        """
        websocket = self.active_connections.get(connection_id)
        if websocket:
            try:
                await websocket.send_text(message.to_json())
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                await self.disconnect(connection_id)

    async def send_to_user(self, message: WebSocketMessage, user_id: str) -> None:
        """
        Send a message to all connections of a user.

        Args:
            message: Message to send
            user_id: Target user ID
        """
        connection_ids = self.user_connections.get(user_id, set())

        for connection_id in list(connection_ids):  # Copy to avoid modification during iteration
            await self.send_personal_message(message, connection_id)

    async def broadcast(self, message: WebSocketMessage) -> None:
        """
        Broadcast a message to all connected clients.

        Args:
            message: Message to broadcast
        """
        for connection_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, connection_id)

    def get_user_id(self, connection_id: str) -> Optional[str]:
        """Get user ID for a connection."""
        return self.connection_users.get(connection_id)

    def get_user_connection_count(self, user_id: str) -> int:
        """Get number of active connections for a user."""
        return len(self.user_connections.get(user_id, set()))


# Global connection manager instance
connection_manager = ConnectionManager()
