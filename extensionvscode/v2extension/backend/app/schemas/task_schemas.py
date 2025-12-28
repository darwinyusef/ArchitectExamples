"""
Pydantic schemas for Task entities.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

from app.models import TaskStatus, TaskType


class TaskCreate(BaseModel):
    """Schema for creating a task."""

    goal_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    task_type: Optional[TaskType] = TaskType.CODE
    priority: Optional[int] = 100
    estimated_hours: Optional[float] = Field(None, ge=0.0)
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskUpdate(BaseModel):
    """Schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    status: Optional[TaskStatus] = None
    task_type: Optional[TaskType] = None
    priority: Optional[int] = None
    estimated_hours: Optional[float] = Field(None, ge=0.0)
    actual_hours: Optional[float] = Field(None, ge=0.0)
    dependencies: Optional[List[str]] = None
    validation_result: Optional[Dict[str, Any]] = None
    ai_feedback: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    """Schema for task responses."""

    id: str
    goal_id: str
    user_id: str
    title: str
    description: str
    task_type: TaskType
    status: TaskStatus
    priority: int
    estimated_hours: Optional[float]
    actual_hours: Optional[float]
    dependencies: List[str]
    validation_result: Optional[Dict[str, Any]]
    ai_feedback: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
