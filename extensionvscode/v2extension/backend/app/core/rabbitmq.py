"""RabbitMQ connection and event publishing/consuming."""

import json
import logging
from typing import Optional, Callable, Any
from aio_pika import connect_robust, Connection, Channel, Exchange, ExchangeType, Message
from aio_pika.abc import AbstractIncomingMessage

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global RabbitMQ connection and channel
_connection: Optional[Connection] = None
_channel: Optional[Channel] = None
_exchange: Optional[Exchange] = None


async def init_rabbitmq() -> None:
    """Initialize RabbitMQ connection and exchange."""
    global _connection, _channel, _exchange

    _connection = await connect_robust(settings.RABBITMQ_URL)
    _channel = await _connection.channel()

    # Declare exchange
    _exchange = await _channel.declare_exchange(
        settings.RABBITMQ_EXCHANGE,
        ExchangeType.TOPIC,
        durable=True,
    )

    logger.info(f"RabbitMQ exchange '{settings.RABBITMQ_EXCHANGE}' declared")


async def close_rabbitmq() -> None:
    """Close RabbitMQ connection."""
    global _connection, _channel, _exchange

    if _channel:
        await _channel.close()
    if _connection:
        await _connection.close()

    _channel = None
    _connection = None
    _exchange = None


def get_exchange() -> Exchange:
    """Get RabbitMQ exchange instance."""
    if _exchange is None:
        raise RuntimeError("RabbitMQ not initialized. Call init_rabbitmq() first.")
    return _exchange


def get_channel() -> Channel:
    """Get RabbitMQ channel instance."""
    if _channel is None:
        raise RuntimeError("RabbitMQ not initialized. Call init_rabbitmq() first.")
    return _channel


class EventPublisher:
    """Publish events to RabbitMQ."""

    def __init__(self) -> None:
        self.exchange = get_exchange()

    async def publish(
        self,
        routing_key: str,
        payload: dict[str, Any],
        headers: Optional[dict[str, str]] = None
    ) -> None:
        """
        Publish an event to RabbitMQ.

        Args:
            routing_key: Event routing key (e.g., 'goal.created', 'task.validated')
            payload: Event payload (will be JSON serialized)
            headers: Optional message headers
        """
        message = Message(
            body=json.dumps(payload).encode(),
            content_type="application/json",
            headers=headers or {},
        )

        await self.exchange.publish(
            message,
            routing_key=routing_key,
        )

        logger.debug(f"Published event: {routing_key}")


class EventConsumer:
    """Consume events from RabbitMQ."""

    def __init__(self, queue_name: str) -> None:
        self.queue_name = queue_name
        self.channel = get_channel()

    async def bind(self, routing_keys: list[str]) -> None:
        """
        Create queue and bind to routing keys.

        Args:
            routing_keys: List of routing keys to subscribe to
                         (e.g., ['goal.*', 'task.validated'])
        """
        exchange = get_exchange()

        # Declare queue
        queue = await self.channel.declare_queue(
            self.queue_name,
            durable=True,
        )

        # Bind to routing keys
        for routing_key in routing_keys:
            await queue.bind(exchange, routing_key=routing_key)
            logger.info(f"Queue '{self.queue_name}' bound to '{routing_key}'")

    async def consume(
        self,
        callback: Callable[[dict[str, Any], str], Any],
        auto_ack: bool = False
    ) -> None:
        """
        Start consuming messages.

        Args:
            callback: Async function to handle messages
                     Signature: async def handler(payload: dict, routing_key: str)
            auto_ack: Whether to auto-acknowledge messages
        """
        queue = await self.channel.get_queue(self.queue_name)

        async def message_handler(message: AbstractIncomingMessage) -> None:
            async with message.process(ignore_processed=auto_ack):
                payload = json.loads(message.body.decode())
                routing_key = message.routing_key or ""

                try:
                    await callback(payload, routing_key)
                    logger.debug(f"Processed message: {routing_key}")
                except Exception as e:
                    logger.error(f"Error processing message {routing_key}: {e}")
                    raise

        await queue.consume(message_handler, no_ack=auto_ack)
        logger.info(f"Started consuming from queue '{self.queue_name}'")


# ==================== Event Types ====================

class EventTypes:
    """Event routing key constants."""

    # User events
    USER_REGISTERED = "user.registered"
    USER_LOGGED_IN = "user.logged_in"
    USER_LOGGED_OUT = "user.logged_out"

    # Goal events
    GOAL_CREATED = "goal.created"
    GOAL_STARTED = "goal.started"
    GOAL_COMPLETED = "goal.completed"
    GOAL_FAILED = "goal.failed"

    # Task events
    TASK_STARTED = "task.started"
    TASK_VALIDATED = "task.validated"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"

    # Code events
    CODE_SUBMITTED = "code.submitted"
    CODE_VALIDATED = "code.validated"

    # Agent events
    FEEDBACK_GENERATED = "feedback.generated"  # Nodo 4
    PERFORMANCE_EVALUATED = "performance.evaluated"  # Nodo 5
    MOOD_DETECTED = "mood.detected"  # Nodo 8
    MOTIVATION_SENT = "motivation.sent"  # Nodo 8
    CONTRACT_CHECKED = "contract.checked"  # Nodo 9
    STATE_CHANGED = "state.changed"  # Nodo 6
