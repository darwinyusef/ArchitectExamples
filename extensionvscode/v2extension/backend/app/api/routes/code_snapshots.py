"""
Code Snapshots API endpoints.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import CodeSnapshotService
from app.schemas.code_snapshot_schemas import CodeSnapshotCreate, CodeSnapshotUpdate, CodeSnapshotResponse

router = APIRouter()


async def get_current_user_id(user_id: str = "test-user-123") -> str:
    """Get current user ID from auth. Simplified for POC."""
    return user_id


@router.post("", response_model=CodeSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def create_snapshot(
    snapshot_data: CodeSnapshotCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new code snapshot."""
    service = CodeSnapshotService(db)
    snapshot = await service.create_snapshot(user_id, snapshot_data)
    return snapshot


@router.get("/{snapshot_id}", response_model=CodeSnapshotResponse)
async def get_snapshot(
    snapshot_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get code snapshot by ID."""
    service = CodeSnapshotService(db)
    snapshot = await service.get_snapshot(snapshot_id, user_id)

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot {snapshot_id} not found"
        )

    return snapshot


@router.get("", response_model=List[CodeSnapshotResponse])
async def list_snapshots(
    task_id: Optional[str] = None,
    language: Optional[str] = None,
    validated_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List code snapshots with filters."""
    service = CodeSnapshotService(db)

    snapshots = await service.list_snapshots(
        user_id=user_id,
        task_id=task_id,
        language=language,
        validated_only=validated_only,
        skip=skip,
        limit=limit
    )

    return snapshots


@router.put("/{snapshot_id}", response_model=CodeSnapshotResponse)
async def update_snapshot(
    snapshot_id: str,
    snapshot_update: CodeSnapshotUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update code snapshot."""
    service = CodeSnapshotService(db)
    snapshot = await service.update_snapshot(snapshot_id, user_id, snapshot_update)

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot {snapshot_id} not found"
        )

    return snapshot


@router.delete("/{snapshot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_snapshot(
    snapshot_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete code snapshot."""
    service = CodeSnapshotService(db)
    deleted = await service.delete_snapshot(snapshot_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot {snapshot_id} not found"
        )


@router.patch("/{snapshot_id}/validation", response_model=CodeSnapshotResponse)
async def update_validation(
    snapshot_id: str,
    validation_data: Dict[str, Any] = Body(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Update validation results for a code snapshot.

    Body should contain:
    {
        "validation_passed": true/false,
        "validation_score": 0.0-1.0,
        "validation_feedback": "...",
        "issues_found": [...]
    }
    """
    service = CodeSnapshotService(db)

    snapshot = await service.update_validation_result(
        snapshot_id=snapshot_id,
        user_id=user_id,
        validation_passed=validation_data.get("validation_passed", False),
        validation_score=validation_data.get("validation_score", 0.0),
        validation_feedback=validation_data.get("validation_feedback", ""),
        issues_found=validation_data.get("issues_found")
    )

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot {snapshot_id} not found"
        )

    return snapshot


@router.get("/tasks/{task_id}/latest", response_model=CodeSnapshotResponse)
async def get_latest_snapshot_for_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get the latest code snapshot for a task."""
    service = CodeSnapshotService(db)
    snapshot = await service.get_latest_for_task(task_id, user_id)

    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No snapshots found for task {task_id}"
        )

    return snapshot
