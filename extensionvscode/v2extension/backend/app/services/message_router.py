"""WebSocket message routing to appropriate handlers."""

import logging
from typing import Any

from app.core.websocket import WebSocketMessage, ConnectionManager

logger = logging.getLogger(__name__)


class MessageRouter:
    """Route incoming WebSocket messages to appropriate handlers."""

    def __init__(
        self,
        connection_id: str,
        user_id: str,
        connection_manager: ConnectionManager
    ):
        self.connection_id = connection_id
        self.user_id = user_id
        self.connection_manager = connection_manager

        # Message type handlers
        self.handlers = {
            "ping": self.handle_ping,
            "goal.create": self.handle_goal_create,
            "goal.start": self.handle_goal_start,
            "task.validate": self.handle_task_validate,
            "code.submit": self.handle_code_submit,
            # Add more handlers as needed
        }

    async def route_message(self, message: WebSocketMessage) -> None:
        """
        Route message to appropriate handler based on type.

        Args:
            message: Incoming WebSocket message
        """
        handler = self.handlers.get(message.type)

        if handler:
            try:
                await handler(message.payload, message.correlation_id)
            except Exception as e:
                logger.error(f"Error handling message type '{message.type}': {e}")
                await self.send_error(f"Error processing {message.type}", message.correlation_id)
        else:
            logger.warning(f"Unknown message type: {message.type}")
            await self.send_error(f"Unknown message type: {message.type}", message.correlation_id)

    async def send_response(
        self,
        type: str,
        payload: dict[str, Any],
        correlation_id: str
    ) -> None:
        """Send response message."""
        response = WebSocketMessage(
            type=type,
            payload=payload,
            correlation_id=correlation_id
        )
        await self.connection_manager.send_personal_message(response, self.connection_id)

    async def send_error(self, error: str, correlation_id: str) -> None:
        """Send error message."""
        await self.send_response(
            "error",
            {"error": error},
            correlation_id
        )

    # ==================== Message Handlers ====================

    async def handle_ping(self, payload: dict[str, Any], correlation_id: str) -> None:
        """Handle ping message."""
        await self.send_response("pong", {"timestamp": payload.get("timestamp")}, correlation_id)

    async def handle_goal_create(self, payload: dict[str, Any], correlation_id: str) -> None:
        """
        Handle goal creation request.

        TODO: Integrate with Nodo 2 (Goal Generator Agent)
        """
        logger.info(f"Goal creation requested by user {self.user_id}")

        # Placeholder response
        await self.send_response(
            "goal.created",
            {
                "goal_id": "placeholder-goal-123",
                "title": payload.get("title", "New Goal"),
                "status": "created"
            },
            correlation_id
        )

    async def handle_goal_start(self, payload: dict[str, Any], correlation_id: str) -> None:
        """
        Handle goal start request.

        TODO: Trigger LangGraph workflow
        """
        goal_id = payload.get("goal_id")
        logger.info(f"Goal {goal_id} started by user {self.user_id}")

        await self.send_response(
            "goal.started",
            {
                "goal_id": goal_id,
                "status": "in_progress"
            },
            correlation_id
        )

    async def handle_task_validate(self, payload: dict[str, Any], correlation_id: str) -> None:
        """
        Handle task validation request.

        TODO: Integrate with Nodo 4 (Feedback Agent)
        """
        task_id = payload.get("task_id")
        code = payload.get("code", "")

        logger.info(f"Task {task_id} validation requested by user {self.user_id}")

        # Send streaming feedback (placeholder)
        await self.send_response(
            "task.validating",
            {"task_id": task_id, "progress": 0.3, "message": "Analyzing code..."},
            correlation_id
        )

        await self.send_response(
            "task.validation_result",
            {
                "task_id": task_id,
                "passed": True,
                "feedback": "Code looks good!",
                "suggestions": []
            },
            correlation_id
        )

    async def handle_code_submit(self, payload: dict[str, Any], correlation_id: str) -> None:
        """
        Handle code submission.

        TODO: Store in database, emit event to RabbitMQ
        """
        code = payload.get("code", "")
        task_id = payload.get("task_id")

        logger.info(f"Code submitted for task {task_id} by user {self.user_id}")

        await self.send_response(
            "code.received",
            {"task_id": task_id, "status": "processing"},
            correlation_id
        )
