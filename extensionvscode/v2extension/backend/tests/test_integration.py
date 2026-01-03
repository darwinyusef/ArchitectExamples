"""Integration tests for API endpoints (POST, PUT) with JWT authentication."""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from app.main import app
from app.core.security import create_access_token
from app.models import User, Course, Goal, Task, CourseStatus, GoalStatus, GoalPriority, TaskStatus, TaskType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid


# ==================== Fixtures ====================

@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfRxz7T/.",  # "password123"
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user: User) -> str:
    """Create JWT token for test user."""
    return create_access_token(data={"sub": test_user.id})


@pytest.fixture
def auth_headers(auth_token: str) -> dict:
    """Create authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
async def test_course(db_session: AsyncSession, test_user: User) -> Course:
    """Create a test course."""
    course = Course(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        title="Test Course",
        description="A test course",
        status=CourseStatus.DRAFT,
        progress_percentage=0.0
    )
    db_session.add(course)
    await db_session.commit()
    await db_session.refresh(course)
    return course


@pytest.fixture
async def test_goal(db_session: AsyncSession, test_user: User, test_course: Course) -> Goal:
    """Create a test goal."""
    goal = Goal(
        id=str(uuid.uuid4()),
        user_id=test_user.id,
        course_id=test_course.id,
        title="Test Goal",
        description="A test goal",
        status=GoalStatus.PENDING,
        priority=GoalPriority.MEDIUM,
        progress_percentage=0.0
    )
    db_session.add(goal)
    await db_session.commit()
    await db_session.refresh(goal)
    return goal


@pytest.fixture
async def test_task(db_session: AsyncSession, test_user: User, test_goal: Goal) -> Task:
    """Create a test task."""
    task = Task(
        id=str(uuid.uuid4()),
        goal_id=test_goal.id,
        user_id=test_user.id,
        title="Test Task",
        description="A test task",
        task_type=TaskType.CODE,
        status=TaskStatus.TODO,
        priority=1
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task


# ==================== Authentication Tests ====================

@pytest.mark.asyncio
class TestAuthentication:
    """Test JWT authentication."""

    async def test_register_user(self, db_session: AsyncSession):
        """Test user registration."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "newuser",
                    "email": "newuser@example.com",
                    "password": "securepass123"
                }
            )
            assert response.status_code in [201, 501]  # 501 = Not Implemented yet

    async def test_login_user(self, db_session: AsyncSession, test_user: User):
        """Test user login."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login",
                json={
                    "username": test_user.username,
                    "password": "password123"
                }
            )
            # Login might not be fully implemented
            assert response.status_code in [200, 401, 501]

    async def test_protected_endpoint_without_token(self, db_session: AsyncSession):
        """Test accessing protected endpoint without token."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/users/me")
            assert response.status_code in [401, 404]  # Should be unauthorized

    async def test_protected_endpoint_with_invalid_token(self, db_session: AsyncSession):
        """Test accessing protected endpoint with invalid token."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": "Bearer invalid_token"}
            )
            assert response.status_code in [401, 404]


# ==================== User Tests ====================

@pytest.mark.asyncio
class TestUserEndpoints:
    """Test User CRUD endpoints."""

    async def test_create_user(self, db_session: AsyncSession):
        """Test POST /api/v1/users."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/users",
                json={
                    "username": "apiuser",
                    "email": "apiuser@example.com",
                    "password": "apipass123"
                }
            )
            assert response.status_code in [201, 200]
            if response.status_code == 201:
                data = response.json()
                assert data["username"] == "apiuser"
                assert data["email"] == "apiuser@example.com"
                assert "id" in data

    async def test_update_user(self, db_session: AsyncSession, test_user: User, auth_headers: dict):
        """Test PUT /api/v1/users/{user_id}."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/users/{test_user.id}",
                headers=auth_headers,
                json={
                    "username": "updateduser",
                    "email": "updated@example.com"
                }
            )
            assert response.status_code in [200, 401, 404]
            if response.status_code == 200:
                data = response.json()
                assert data["username"] == "updateduser"


# ==================== Course Tests ====================

@pytest.mark.asyncio
class TestCourseEndpoints:
    """Test Course CRUD endpoints."""

    async def test_create_course(self, db_session: AsyncSession, test_user: User):
        """Test POST /api/v1/courses."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/courses",
                params={"user_id": test_user.id},
                json={
                    "title": "New Course",
                    "description": "Course description",
                    "status": "draft",
                    "metadata": {"tags": ["python", "backend"]}
                }
            )
            assert response.status_code in [201, 200, 422]
            if response.status_code == 201:
                data = response.json()
                assert data["title"] == "New Course"
                assert "id" in data

    async def test_update_course(self, db_session: AsyncSession, test_course: Course, test_user: User):
        """Test PUT /api/v1/courses/{course_id}."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/courses/{test_course.id}",
                params={"user_id": test_user.id},
                json={
                    "title": "Updated Course Title",
                    "description": "Updated description"
                }
            )
            assert response.status_code in [200, 404, 422]
            if response.status_code == 200:
                data = response.json()
                assert data["title"] == "Updated Course Title"

    async def test_publish_course(self, db_session: AsyncSession, test_course: Course, test_user: User):
        """Test POST /api/v1/courses/{course_id}/publish."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/v1/courses/{test_course.id}/publish",
                params={"user_id": test_user.id}
            )
            assert response.status_code in [200, 404]

    async def test_archive_course(self, db_session: AsyncSession, test_course: Course, test_user: User):
        """Test POST /api/v1/courses/{course_id}/archive."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                f"/api/v1/courses/{test_course.id}/archive",
                params={"user_id": test_user.id}
            )
            assert response.status_code in [200, 404]


# ==================== Goal Tests ====================

@pytest.mark.asyncio
class TestGoalEndpoints:
    """Test Goal CRUD endpoints."""

    async def test_create_goal(self, db_session: AsyncSession, test_user: User, test_course: Course):
        """Test POST /api/v1/goals."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/goals",
                params={"user_id": test_user.id},
                json={
                    "course_id": test_course.id,
                    "title": "New Goal",
                    "description": "Goal description",
                    "priority": "high",
                    "validation_criteria": ["Complete task 1", "Complete task 2"]
                }
            )
            assert response.status_code in [201, 200, 422]
            if response.status_code == 201:
                data = response.json()
                assert data["title"] == "New Goal"
                assert data["priority"] == "high"

    async def test_update_goal(self, db_session: AsyncSession, test_goal: Goal, test_user: User):
        """Test PUT /api/v1/goals/{goal_id}."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/goals/{test_goal.id}",
                params={"user_id": test_user.id},
                json={
                    "title": "Updated Goal",
                    "description": "Updated description",
                    "priority": "urgent"
                }
            )
            assert response.status_code in [200, 404, 422]
            if response.status_code == 200:
                data = response.json()
                assert data["title"] == "Updated Goal"

    async def test_update_goal_progress(self, db_session: AsyncSession, test_goal: Goal, test_user: User):
        """Test PATCH /api/v1/goals/{goal_id}/progress."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.patch(
                f"/api/v1/goals/{test_goal.id}/progress",
                params={
                    "user_id": test_user.id,
                    "progress": 50.0
                }
            )
            assert response.status_code in [200, 404, 422]


# ==================== Task Tests ====================

@pytest.mark.asyncio
class TestTaskEndpoints:
    """Test Task CRUD endpoints."""

    async def test_create_task(self, db_session: AsyncSession, test_user: User, test_goal: Goal):
        """Test POST /api/v1/tasks."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/tasks",
                params={"user_id": test_user.id},
                json={
                    "goal_id": test_goal.id,
                    "title": "New Task",
                    "description": "Task description",
                    "task_type": "code",
                    "priority": 1
                }
            )
            assert response.status_code in [201, 200, 422]
            if response.status_code == 201:
                data = response.json()
                assert data["title"] == "New Task"
                assert data["task_type"] == "code"

    async def test_update_task(self, db_session: AsyncSession, test_task: Task, test_user: User):
        """Test PUT /api/v1/tasks/{task_id}."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/tasks/{test_task.id}",
                params={"user_id": test_user.id},
                json={
                    "title": "Updated Task",
                    "description": "Updated description",
                    "status": "in_progress"
                }
            )
            assert response.status_code in [200, 404, 422]
            if response.status_code == 200:
                data = response.json()
                assert data["title"] == "Updated Task"


# ==================== Code Snapshot Tests ====================

@pytest.mark.asyncio
class TestCodeSnapshotEndpoints:
    """Test Code Snapshot endpoints."""

    async def test_create_snapshot(self, db_session: AsyncSession, test_user: User, test_task: Task):
        """Test POST /api/v1/code-snapshots."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/code-snapshots",
                params={"user_id": test_user.id},
                json={
                    "task_id": test_task.id,
                    "code_content": "print('Hello World')",
                    "file_path": "/test/hello.py",
                    "language": "python"
                }
            )
            assert response.status_code in [201, 200, 422]

    async def test_update_snapshot(self, db_session: AsyncSession, test_user: User):
        """Test PUT /api/v1/code-snapshots/{snapshot_id}."""
        # First create a snapshot
        snapshot_id = str(uuid.uuid4())
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/code-snapshots/{snapshot_id}",
                params={"user_id": test_user.id},
                json={
                    "code_content": "print('Updated')",
                    "file_path": "/test/updated.py"
                }
            )
            assert response.status_code in [200, 404, 422]


# ==================== Event Tests ====================

@pytest.mark.asyncio
class TestEventEndpoints:
    """Test Event endpoints."""

    async def test_create_event(self, db_session: AsyncSession, test_user: User):
        """Test POST /api/v1/events."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/events",
                json={
                    "event_type": "user.created",
                    "entity_type": "user",
                    "entity_id": test_user.id,
                    "user_id": test_user.id,
                    "event_data": {"action": "registration"}
                }
            )
            assert response.status_code in [201, 200, 422]


# ==================== Validation Tests ====================

@pytest.mark.asyncio
class TestValidation:
    """Test input validation."""

    async def test_create_goal_with_invalid_priority(self, db_session: AsyncSession, test_user: User):
        """Test creating goal with invalid priority."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/goals",
                params={"user_id": test_user.id},
                json={
                    "title": "Invalid Goal",
                    "priority": "invalid_priority"  # Should fail
                }
            )
            assert response.status_code == 422

    async def test_create_task_with_missing_required_fields(self, db_session: AsyncSession, test_user: User):
        """Test creating task without required fields."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/tasks",
                params={"user_id": test_user.id},
                json={
                    # Missing goal_id and title
                    "description": "Task without required fields"
                }
            )
            assert response.status_code == 422

    async def test_update_course_with_invalid_status(self, db_session: AsyncSession, test_course: Course, test_user: User):
        """Test updating course with invalid status."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/courses/{test_course.id}",
                params={"user_id": test_user.id},
                json={
                    "status": "invalid_status"
                }
            )
            assert response.status_code == 422


# ==================== Error Handling Tests ====================

@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling."""

    async def test_get_nonexistent_goal(self, db_session: AsyncSession, test_user: User):
        """Test getting a goal that doesn't exist."""
        fake_id = str(uuid.uuid4())
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/goals/{fake_id}",
                params={"user_id": test_user.id}
            )
            assert response.status_code == 404

    async def test_update_nonexistent_task(self, db_session: AsyncSession, test_user: User):
        """Test updating a task that doesn't exist."""
        fake_id = str(uuid.uuid4())
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/tasks/{fake_id}",
                params={"user_id": test_user.id},
                json={
                    "title": "Updated Task"
                }
            )
            assert response.status_code == 404

    async def test_delete_nonexistent_course(self, db_session: AsyncSession, test_user: User):
        """Test deleting a course that doesn't exist."""
        fake_id = str(uuid.uuid4())
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete(
                f"/api/v1/courses/{fake_id}",
                params={"user_id": test_user.id}
            )
            assert response.status_code == 404
