"""
Pydantic schemas for Goal entities.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.models import GoalStatus, GoalPriority


class GoalCreate(BaseModel):
    """Schema for creating a goal."""

    course_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    priority: Optional[GoalPriority] = GoalPriority.MEDIUM
    validation_criteria: Optional[List[str]] = None
    ai_generated: bool = False
    due_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class GoalUpdate(BaseModel):
    """Schema for updating a goal."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[GoalStatus] = None
    priority: Optional[GoalPriority] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    validation_criteria: Optional[List[str]] = None
    due_date: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class GoalResponse(BaseModel):
    """Schema for goal responses."""

    id: str
    user_id: str
    course_id: Optional[str]
    title: str
    description: str
    status: GoalStatus
    priority: GoalPriority
    progress_percentage: float
    ai_generated: bool
    validation_criteria: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
