"""
Pydantic schemas for CodeSnapshot entities.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class CodeSnapshotCreate(BaseModel):
    """Schema for creating a code snapshot."""

    task_id: str
    file_path: str = Field(..., min_length=1)
    language: str = Field(..., min_length=1)
    code_content: str = Field(..., min_length=1)
    diff_from_previous: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CodeSnapshotUpdate(BaseModel):
    """Schema for updating a code snapshot."""

    file_path: Optional[str] = Field(None, min_length=1)
    code_content: Optional[str] = Field(None, min_length=1)
    diff_from_previous: Optional[str] = None
    validation_passed: Optional[bool] = None
    validation_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    validation_feedback: Optional[str] = None
    issues_found: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class CodeSnapshotResponse(BaseModel):
    """Schema for code snapshot responses."""

    id: str
    task_id: str
    user_id: str
    file_path: str
    language: str
    code_content: str
    diff_from_previous: Optional[str]
    validation_passed: Optional[bool]
    validation_score: Optional[float]
    validation_feedback: Optional[str]
    issues_found: Optional[List[Dict[str, Any]]]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
