"""
Courses API endpoints (TEMPORAL - POC).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import CourseService
from app.schemas.course_schemas import CourseCreate, CourseUpdate, CourseResponse
from app.models import CourseStatus

router = APIRouter()


async def get_current_user_id(user_id: str = "test-user-123") -> str:
    """Get current user ID from auth. Simplified for POC."""
    return user_id


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Create a new course."""
    service = CourseService(db)
    course = await service.create_course(user_id, course_data)
    return course


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get course by ID."""
    service = CourseService(db)
    course = await service.get_course(course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    return course


@router.get("", response_model=List[CourseResponse])
async def list_courses(
    status_filter: Optional[str] = None,
    user_id_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List courses with filters."""
    service = CourseService(db)

    # Parse status filter
    course_status = None
    if status_filter:
        try:
            course_status = CourseStatus[status_filter.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )

    courses = await service.list_courses(
        status=course_status,
        user_id=user_id_filter,
        skip=skip,
        limit=limit
    )

    return courses


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    course_update: CourseUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update course."""
    service = CourseService(db)
    course = await service.update_course(course_id, course_update)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    return course


@router.post("/{course_id}/publish", response_model=CourseResponse)
async def publish_course(
    course_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Publish a course (change status to ACTIVE)."""
    service = CourseService(db)

    # Verify ownership
    course = await service.get_course(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    if course.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only publish your own courses"
        )

    course = await service.publish_course(course_id)
    return course


@router.post("/{course_id}/archive", response_model=CourseResponse)
async def archive_course(
    course_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Archive a course."""
    service = CourseService(db)

    # Verify ownership
    course = await service.get_course(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course {course_id} not found"
        )

    if course.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only archive your own courses"
        )

    course = await service.archive_course(course_id)
    return course
