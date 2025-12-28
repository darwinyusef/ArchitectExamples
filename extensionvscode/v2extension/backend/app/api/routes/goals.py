"""
Goals API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import GoalService
from app.schemas.goal_schemas import GoalCreate, GoalUpdate, GoalResponse
from app.models import GoalStatus

router = APIRouter()


# Helper to get user_id from header (simplified for POC)
async def get_current_user_id(user_id: str = "test-user-123") -> str:
    """Get current user ID from auth. Simplified for POC."""
    return user_id


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_data: GoalCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new goal.

    Args:
        goal_data: Goal creation data
        user_id: Current user ID (from auth)
        db: Database session

    Returns:
        Created goal
    """
    service = GoalService(db)
    goal = await service.create_goal(user_id, goal_data)
    return goal


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get goal by ID.

    Args:
        goal_id: Goal ID
        user_id: Current user ID (from auth)
        db: Database session

    Returns:
        Goal details

    Raises:
        404: Goal not found
    """
    service = GoalService(db)
    goal = await service.get_goal(goal_id, user_id)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal {goal_id} not found"
        )

    return goal


@router.get("", response_model=List[GoalResponse])
async def list_goals(
    status_filter: Optional[str] = None,
    course_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    List goals with filters.

    Args:
        status_filter: Filter by status (pending, in_progress, completed, etc.)
        course_id: Filter by course ID
        skip: Pagination offset
        limit: Pagination limit
        user_id: Current user ID (from auth)
        db: Database session

    Returns:
        List of goals
    """
    service = GoalService(db)

    # Parse status filter
    goal_status = None
    if status_filter:
        try:
            goal_status = GoalStatus[status_filter.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )

    goals = await service.list_goals(
        user_id=user_id,
        status=goal_status,
        course_id=course_id,
        skip=skip,
        limit=limit
    )

    return goals


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    goal_update: GoalUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Update goal.

    Args:
        goal_id: Goal ID
        goal_update: Goal update data
        user_id: Current user ID (from auth)
        db: Database session

    Returns:
        Updated goal

    Raises:
        404: Goal not found
    """
    service = GoalService(db)
    goal = await service.update_goal(goal_id, user_id, goal_update)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal {goal_id} not found"
        )

    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete goal.

    Args:
        goal_id: Goal ID
        user_id: Current user ID (from auth)
        db: Database session

    Raises:
        404: Goal not found
    """
    service = GoalService(db)
    deleted = await service.delete_goal(goal_id, user_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal {goal_id} not found"
        )


@router.patch("/{goal_id}/progress", response_model=GoalResponse)
async def update_goal_progress(
    goal_id: str,
    progress_percentage: float,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Update goal progress.

    Args:
        goal_id: Goal ID
        progress_percentage: Progress 0-100
        user_id: Current user ID (from auth)
        db: Database session

    Returns:
        Updated goal

    Raises:
        404: Goal not found
        400: Invalid progress value
    """
    if progress_percentage < 0 or progress_percentage > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Progress must be between 0 and 100"
        )

    service = GoalService(db)
    goal = await service.update_progress(goal_id, user_id, progress_percentage)

    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal {goal_id} not found"
        )

    return goal
