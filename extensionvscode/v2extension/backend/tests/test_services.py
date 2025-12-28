"""Tests for CRUD services."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.services.goal_service import GoalService
from app.services.task_service import TaskService
from app.models import GoalStatus, GoalPriority, TaskStatus, TaskType


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    session.rollback = AsyncMock()

    return session


@pytest.mark.asyncio
async def test_goal_service_create_goal(mock_db_session):
    """Test creating a goal."""
    service = GoalService(mock_db_session)

    goal_data = {
        "title": "Learn Python",
        "description": "Master Python programming",
        "user_id": "user_123",
        "course_id": "course_456",
        "priority": GoalPriority.HIGH,
    }

    # Mock the execute result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    goal = await service.create_goal(**goal_data)

    assert goal.title == "Learn Python"
    assert goal.user_id == "user_123"
    assert goal.status == GoalStatus.NOT_STARTED
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_task_service_create_task(mock_db_session):
    """Test creating a task."""
    service = TaskService(mock_db_session)

    task_data = {
        "title": "Complete tutorial",
        "description": "Finish Python basics tutorial",
        "goal_id": "goal_123",
        "user_id": "user_123",
        "task_type": TaskType.LEARNING,
    }

    # Mock the execute result
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    task = await service.create_task(**task_data)

    assert task.title == "Complete tutorial"
    assert task.user_id == "user_123"
    assert task.status == TaskStatus.TODO
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_goal_service_update_goal(mock_db_session):
    """Test updating a goal."""
    service = GoalService(mock_db_session)

    # Mock existing goal
    existing_goal = MagicMock()
    existing_goal.id = "goal_123"
    existing_goal.title = "Old Title"
    existing_goal.status = GoalStatus.NOT_STARTED
    existing_goal.metadata = {}

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=existing_goal)
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    updated_goal = await service.update_goal(
        goal_id="goal_123",
        user_id="user_123",
        title="New Title",
        status=GoalStatus.IN_PROGRESS
    )

    assert updated_goal.title == "New Title"
    assert updated_goal.status == GoalStatus.IN_PROGRESS
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_task_service_complete_task(mock_db_session):
    """Test completing a task."""
    service = TaskService(mock_db_session)

    # Mock existing task
    existing_task = MagicMock()
    existing_task.id = "task_123"
    existing_task.status = TaskStatus.IN_PROGRESS
    existing_task.metadata = {}

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=existing_task)
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    completed_task = await service.complete_task(
        task_id="task_123",
        user_id="user_123"
    )

    assert completed_task.status == TaskStatus.COMPLETED
    assert completed_task.completed_at is not None
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_goal_service_list_goals(mock_db_session):
    """Test listing goals."""
    service = GoalService(mock_db_session)

    # Mock goals
    mock_goals = [
        MagicMock(id="goal_1", title="Goal 1"),
        MagicMock(id="goal_2", title="Goal 2"),
    ]

    mock_result = MagicMock()
    mock_result.scalars = MagicMock(return_value=MagicMock(all=MagicMock(return_value=mock_goals)))
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    goals = await service.list_goals(user_id="user_123")

    assert len(goals) == 2
    assert goals[0].id == "goal_1"
    assert goals[1].id == "goal_2"


@pytest.mark.asyncio
async def test_goal_service_delete_goal(mock_db_session):
    """Test deleting a goal."""
    service = GoalService(mock_db_session)

    # Mock existing goal
    existing_goal = MagicMock()
    existing_goal.id = "goal_123"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=existing_goal)
    mock_db_session.execute = AsyncMock(return_value=mock_result)
    mock_db_session.delete = AsyncMock()

    await service.delete_goal(
        goal_id="goal_123",
        user_id="user_123"
    )

    mock_db_session.delete.assert_called_once_with(existing_goal)
    mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_goal_service_not_found(mock_db_session):
    """Test goal not found scenario."""
    service = GoalService(mock_db_session)

    # Mock no goal found
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_db_session.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(ValueError, match="Goal not found"):
        await service.update_goal(
            goal_id="nonexistent",
            user_id="user_123",
            title="New Title"
        )
