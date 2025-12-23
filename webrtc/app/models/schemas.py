from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    status: str = Field(default="active", pattern="^(active|inactive|pending)$")


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(active|inactive|pending)$")


class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WebRTCSignal(BaseModel):
    """Modelo para señales WebRTC"""
    type: str  # offer, answer, ice-candidate
    data: dict
    room_id: str
    peer_id: str
