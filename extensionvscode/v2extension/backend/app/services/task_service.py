"""
Task Service - CRUD operations for tasks.
"""

from typing import List, Optional
from datetime import datetime
import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task, TaskStatus, TaskType, Embedding
from app.schemas.task_schemas import TaskCreate, TaskUpdate
from app.agents.tools.rag_tools import RAGTools


class TaskService:
    """Service for managing tasks."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag = RAGTools()

    async def create_task(
        self,
        user_id: str,
        task_data: TaskCreate,
        generate_embedding: bool = True
    ) -> Task:
        """
        Create a new task.

        Args:
            user_id: User ID
            task_data: Task creation data
            generate_embedding: Whether to generate embedding for RAG

        Returns:
            Created task
        """
        task_id = str(uuid.uuid4())

        task = Task(
            id=task_id,
            goal_id=task_data.goal_id,
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            task_type=task_data.task_type or TaskType.CODE,
            status=TaskStatus.TODO,
            priority=task_data.priority or 100,
            estimated_hours=task_data.estimated_hours,
            dependencies=task_data.dependencies or [],
            metadata=task_data.metadata or {}
        )

        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        # Generate embedding for RAG
        if generate_embedding and task.description:
            await self._create_embedding(task)

        return task

    async def get_task(self, task_id: str, user_id: str) -> Optional[Task]:
        """Get task by ID."""
        result = await self.db.execute(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_tasks(
        self,
        user_id: str,
        goal_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """List tasks with filters."""
        query = select(Task).where(Task.user_id == user_id)

        if goal_id:
            query = query.where(Task.goal_id == goal_id)

        if status:
            query = query.where(Task.status == status)

        if task_type:
            query = query.where(Task.task_type == task_type)

        query = query.order_by(Task.priority, Task.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_task(
        self,
        task_id: str,
        user_id: str,
        task_update: TaskUpdate
    ) -> Optional[Task]:
        """Update task."""
        task = await self.get_task(task_id, user_id)
        if not task:
            return None

        update_data = task_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(task, field, value)

        # Handle status transitions
        if task_update.status:
            if task_update.status == TaskStatus.IN_PROGRESS and not task.started_at:
                task.started_at = datetime.utcnow()
            elif task_update.status == TaskStatus.COMPLETED and not task.completed_at:
                task.completed_at = datetime.utcnow()

        task.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(task)

        # Update embedding if description changed
        if task_update.description:
            await self._update_embedding(task)

        return task

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete task."""
        result = await self.db.execute(
            delete(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    async def update_validation(
        self,
        task_id: str,
        user_id: str,
        validation_result: dict,
        ai_feedback: Optional[str] = None
    ) -> Optional[Task]:
        """Update task validation results."""
        task = await self.get_task(task_id, user_id)
        if not task:
            return None

        task.validation_result = validation_result
        if ai_feedback:
            task.ai_feedback = ai_feedback

        task.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(task)

        return task

    async def _create_embedding(self, task: Task) -> None:
        """Create embedding for task (for RAG)."""
        content = f"Task: {task.title}\n\nDescription: {task.description}\n\nType: {task.task_type.value}"

        embedding_vector = await self.rag._generate_embedding(content)

        embedding = Embedding(
            id=str(uuid.uuid4()),
            user_id=task.user_id,
            entity_type="task",
            entity_id=task.id,
            content=content,
            embedding=embedding_vector,
            model="text-embedding-3-small",
            metadata={
                "task_type": task.task_type.value,
                "task_status": task.status.value
            }
        )

        self.db.add(embedding)
        await self.db.commit()

    async def _update_embedding(self, task: Task) -> None:
        """Update embedding when task description changes."""
        # Delete old embedding
        await self.db.execute(
            delete(Embedding).where(
                Embedding.entity_type == "task",
                Embedding.entity_id == task.id
            )
        )

        # Create new embedding
        await self._create_embedding(task)
