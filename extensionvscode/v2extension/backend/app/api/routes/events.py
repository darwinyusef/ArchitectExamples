"""
Events API endpoints.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import EventService
from app.schemas.event_schemas import EventCreate, EventResponse
from app.models import EventType

router = APIRouter()


async def get_current_user_id(user_id: str = "test-user-123") -> str:
    """Get current user ID from auth. Simplified for POC."""
    return user_id


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new event.

    This will persist the event to:
    1. PostgreSQL
    2. Parquet file (partitioned by date)
    3. RabbitMQ (pub/sub)
    """
    service = EventService(db)

    event = await service.create_event(
        user_id=user_id,
        event_type=event_data.event_type,
        entity_type=event_data.entity_type,
        entity_id=event_data.entity_id,
        event_data=event_data.event_data,
        metadata=event_data.metadata
    )

    return event


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get event by ID."""
    service = EventService(db)
    event = await service.get_event(event_id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {event_id} not found"
        )

    return event


@router.get("", response_model=List[EventResponse])
async def list_events(
    user_id_filter: Optional[str] = None,
    event_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List events with filters."""
    service = EventService(db)

    # Parse event_type
    parsed_event_type = None
    if event_type:
        try:
            parsed_event_type = EventType[event_type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event_type: {event_type}"
            )

    events = await service.list_events(
        user_id=user_id_filter,
        event_type=parsed_event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )

    return events


@router.get("/entities/{entity_type}/{entity_id}/history", response_model=List[EventResponse])
async def get_entity_history(
    entity_type: str,
    entity_id: str,
    user_id_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get complete event history for an entity."""
    service = EventService(db)

    events = await service.get_entity_history(
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id_filter
    )

    return events


@router.post("/replay", response_model=Dict[str, Any])
async def replay_events(
    replay_data: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Replay events to reconstruct entity state.

    Body should contain:
    {
        "entity_type": "goal",
        "entity_id": "goal_123",
        "target_timestamp": "2025-12-28T10:00:00Z" (optional)
    }
    """
    service = EventService(db)

    entity_type = replay_data.get("entity_type")
    entity_id = replay_data.get("entity_id")
    target_timestamp_str = replay_data.get("target_timestamp")

    if not entity_type or not entity_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="entity_type and entity_id are required"
        )

    target_timestamp = None
    if target_timestamp_str:
        try:
            target_timestamp = datetime.fromisoformat(target_timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid timestamp format. Use ISO 8601 format."
            )

    result = await service.replay_events(
        entity_type=entity_type,
        entity_id=entity_id,
        target_timestamp=target_timestamp
    )

    return result
