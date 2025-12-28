"""
Pydantic schemas for Course entities.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

from app.models import CourseStatus


class CourseCreate(BaseModel):
    """Schema for creating a course."""

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    syllabus: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class CourseUpdate(BaseModel):
    """Schema for updating a course."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[CourseStatus] = None
    syllabus: Optional[Dict[str, Any]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class CourseResponse(BaseModel):
    """Schema for course responses."""

    id: str
    user_id: str
    title: str
    description: str
    status: CourseStatus
    syllabus: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
