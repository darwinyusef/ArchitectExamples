"""
Tasks API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import TaskService
from app.schemas.task_schemas import TaskCreate, TaskUpdate, TaskResponse
from app.models import TaskStatus, TaskType

router = APIRouter()


async def get_current_user_id(user_id: str = "test-user-123") -> str:
    """Get current user ID from auth. Simplified for POC."""
    return user_id


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    service = TaskService(db)
    task = await service.create_task(user_id, task_data)
    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Get task by ID."""
    service = TaskService(db)
    task = await service.get_task(task_id, user_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return task


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    goal_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    task_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """List tasks with filters."""
    service = TaskService(db)

    # Parse filters
    parsed_status = None
    if status_filter:
        try:
            parsed_status = TaskStatus[status_filter.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )

    parsed_task_type = None
    if task_type:
        try:
            parsed_task_type = TaskType[task_type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid task_type: {task_type}"
            )

    tasks = await service.list_tasks(
        user_id=user_id,
        goal_id=goal_id,
        status=parsed_status,
        task_type=parsed_task_type,
        skip=skip,
        limit=limit
    )

    return tasks


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Update task."""
    service = TaskService(db)
    task = await service.update_task(task_id, user_id, task_update)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )

    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Delete task."""
    service = TaskService(db)
    deleted = await service.delete_task(task_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
