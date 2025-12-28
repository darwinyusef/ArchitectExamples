"""
Pydantic schemas for Event entities.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.models import EventType


class EventCreate(BaseModel):
    """Schema for creating an event."""

    event_type: EventType
    entity_type: str
    entity_id: str
    event_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class EventResponse(BaseModel):
    """Schema for event responses."""

    id: str
    user_id: str
    event_type: EventType
    entity_type: str
    entity_id: str
    event_data: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime

    class Config:
        from_attributes = True
