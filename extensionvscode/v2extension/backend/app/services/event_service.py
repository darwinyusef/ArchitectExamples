"""
Event Service - Event sourcing operations.

Este servicio maneja la persistencia triple:
1. PostgreSQL (base de datos relacional)
2. Parquet (archivos particionados por fecha)
3. RabbitMQ (publicación de eventos)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import os
import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import pyarrow as pa
import pyarrow.parquet as pq
import aio_pika

from app.models import Event, EventType
from app.schemas.parquet_schemas import (
    BaseEvent,
    UserEvent,
    GoalEvent,
    TaskEvent,
    CodeEvent,
    AIEvent,
    get_schema_for_event_type,
    get_parquet_path
)
from app.core.config import settings


class EventService:
    """Service for event sourcing with triple persistence."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None

    async def _get_rabbitmq_channel(self):
        """Get or create RabbitMQ channel."""
        if not self.rabbitmq_channel:
            self.rabbitmq_connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URL
            )
            self.rabbitmq_channel = await self.rabbitmq_connection.channel()

        return self.rabbitmq_channel

    async def create_event(
        self,
        user_id: str,
        event_type: EventType,
        entity_type: str,
        entity_id: str,
        event_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """
        Create event with triple persistence:
        1. Save to PostgreSQL
        2. Append to Parquet file
        3. Publish to RabbitMQ

        Args:
            user_id: User ID
            event_type: Type of event
            entity_type: Type of entity (goal, task, code_snapshot, etc.)
            entity_id: ID of the entity
            event_data: Event payload
            metadata: Optional metadata

        Returns:
            Created event
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()

        # 1. Save to PostgreSQL
        event = Event(
            id=event_id,
            user_id=user_id,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            event_data=event_data,
            metadata=metadata or {},
            timestamp=timestamp
        )

        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        # 2. Save to Parquet (async in background would be better)
        await self._save_to_parquet(event)

        # 3. Publish to RabbitMQ
        await self._publish_to_rabbitmq(event)

        return event

    async def get_event(self, event_id: str) -> Optional[Event]:
        """Get event by ID."""
        result = await self.db.execute(
            select(Event).where(Event.id == event_id)
        )
        return result.scalar_one_or_none()

    async def list_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[EventType] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Event]:
        """List events with filters."""
        query = select(Event)

        if user_id:
            query = query.where(Event.user_id == user_id)

        if event_type:
            query = query.where(Event.event_type == event_type)

        if entity_type:
            query = query.where(Event.entity_type == entity_type)

        if entity_id:
            query = query.where(Event.entity_id == entity_id)

        if start_date:
            query = query.where(Event.timestamp >= start_date)

        if end_date:
            query = query.where(Event.timestamp <= end_date)

        query = query.order_by(Event.timestamp.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_entity_history(
        self,
        entity_type: str,
        entity_id: str,
        user_id: Optional[str] = None
    ) -> List[Event]:
        """Get complete event history for an entity."""
        query = select(Event).where(
            Event.entity_type == entity_type,
            Event.entity_id == entity_id
        )

        if user_id:
            query = query.where(Event.user_id == user_id)

        query = query.order_by(Event.timestamp.asc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _save_to_parquet(self, event: Event) -> None:
        """
        Save event to Parquet file.

        Files are partitioned by year/month/day.
        """
        # Get Parquet path for this event
        parquet_path = get_parquet_path(
            event_type=event.event_type.value,
            timestamp=event.timestamp
        )

        # Ensure directory exists
        os.makedirs(os.path.dirname(parquet_path), exist_ok=True)

        # Get schema for this event type
        schema = get_schema_for_event_type(event.event_type.value)

        # Build record based on event type
        record = {
            "event_id": event.id,
            "user_id": event.user_id,
            "entity_id": event.entity_id,
            "timestamp": event.timestamp.isoformat(),
            "year": event.timestamp.year,
            "month": event.timestamp.month,
            "day": event.timestamp.day,
            **event.event_data  # Unpack event data
        }

        # Create PyArrow table
        table = pa.Table.from_pylist([record], schema=schema)

        # Append to Parquet file (or create if doesn't exist)
        if os.path.exists(parquet_path):
            # Append to existing file
            existing_table = pq.read_table(parquet_path)
            combined_table = pa.concat_tables([existing_table, table])
            pq.write_table(combined_table, parquet_path)
        else:
            # Create new file
            pq.write_table(table, parquet_path)

    async def _publish_to_rabbitmq(self, event: Event) -> None:
        """
        Publish event to RabbitMQ.

        Exchange: events
        Routing key: {event_type}.{entity_type}
        """
        try:
            channel = await self._get_rabbitmq_channel()

            # Declare exchange
            exchange = await channel.declare_exchange(
                "events",
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

            # Build message
            message_body = {
                "event_id": event.id,
                "user_id": event.user_id,
                "event_type": event.event_type.value,
                "entity_type": event.entity_type,
                "entity_id": event.entity_id,
                "event_data": event.event_data,
                "metadata": event.metadata,
                "timestamp": event.timestamp.isoformat()
            }

            message = aio_pika.Message(
                body=json.dumps(message_body).encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            # Routing key: event_type.entity_type
            routing_key = f"{event.event_type.value}.{event.entity_type}"

            # Publish
            await exchange.publish(
                message,
                routing_key=routing_key
            )

        except Exception as e:
            # Log error but don't fail the event creation
            print(f"Error publishing to RabbitMQ: {e}")

    async def close(self):
        """Close RabbitMQ connection."""
        if self.rabbitmq_connection:
            await self.rabbitmq_connection.close()

    async def replay_events(
        self,
        entity_type: str,
        entity_id: str,
        target_timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Replay events to reconstruct entity state at a specific point in time.

        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            target_timestamp: Point in time to reconstruct (None = current)

        Returns:
            Reconstructed entity state
        """
        query = select(Event).where(
            Event.entity_type == entity_type,
            Event.entity_id == entity_id
        )

        if target_timestamp:
            query = query.where(Event.timestamp <= target_timestamp)

        query = query.order_by(Event.timestamp.asc())

        result = await self.db.execute(query)
        events = result.scalars().all()

        # Reconstruct state by applying events
        state = {}
        for event in events:
            # Apply event data to state
            state.update(event.event_data)

        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "reconstructed_at": target_timestamp.isoformat() if target_timestamp else "current",
            "event_count": len(events),
            "state": state
        }
