"""
Goal Service - CRUD operations for goals.
"""

from typing import List, Optional
from datetime import datetime
import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Goal, GoalStatus, GoalPriority, Embedding
from app.schemas.goal_schemas import GoalCreate, GoalUpdate, GoalResponse
from app.agents.tools.rag_tools import RAGTools


class GoalService:
    """Service for managing goals."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag = RAGTools()

    async def create_goal(
        self,
        user_id: str,
        goal_data: GoalCreate,
        generate_embedding: bool = True
    ) -> Goal:
        """
        Create a new goal.

        Args:
            user_id: User ID
            goal_data: Goal creation data
            generate_embedding: Whether to generate embedding for RAG

        Returns:
            Created goal
        """
        goal_id = str(uuid.uuid4())

        goal = Goal(
            id=goal_id,
            user_id=user_id,
            course_id=goal_data.course_id,
            title=goal_data.title,
            description=goal_data.description,
            status=GoalStatus.PENDING,
            priority=goal_data.priority or GoalPriority.MEDIUM,
            progress_percentage=0.0,
            ai_generated=goal_data.ai_generated or False,
            validation_criteria=goal_data.validation_criteria,
            metadata=goal_data.metadata or {},
            due_date=goal_data.due_date
        )

        self.db.add(goal)
        await self.db.commit()
        await self.db.refresh(goal)

        # Generate embedding for RAG
        if generate_embedding and goal.description:
            await self._create_embedding(goal)

        return goal

    async def get_goal(self, goal_id: str, user_id: str) -> Optional[Goal]:
        """Get goal by ID."""
        result = await self.db.execute(
            select(Goal).where(
                Goal.id == goal_id,
                Goal.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def list_goals(
        self,
        user_id: str,
        status: Optional[GoalStatus] = None,
        course_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Goal]:
        """List goals with filters."""
        query = select(Goal).where(Goal.user_id == user_id)

        if status:
            query = query.where(Goal.status == status)

        if course_id:
            query = query.where(Goal.course_id == course_id)

        query = query.order_by(Goal.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_goal(
        self,
        goal_id: str,
        user_id: str,
        goal_update: GoalUpdate
    ) -> Optional[Goal]:
        """Update goal."""
        goal = await self.get_goal(goal_id, user_id)
        if not goal:
            return None

        update_data = goal_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(goal, field, value)

        # Handle status transitions
        if goal_update.status:
            if goal_update.status == GoalStatus.IN_PROGRESS and not goal.started_at:
                goal.started_at = datetime.utcnow()
            elif goal_update.status == GoalStatus.COMPLETED:
                goal.completed_at = datetime.utcnow()
                goal.progress_percentage = 100.0

        goal.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(goal)

        # Update embedding if description changed
        if goal_update.description:
            await self._update_embedding(goal)

        return goal

    async def delete_goal(self, goal_id: str, user_id: str) -> bool:
        """Delete goal."""
        result = await self.db.execute(
            delete(Goal).where(
                Goal.id == goal_id,
                Goal.user_id == user_id
            )
        )
        await self.db.commit()
        return result.rowcount > 0

    async def update_progress(
        self,
        goal_id: str,
        user_id: str,
        progress_percentage: float
    ) -> Optional[Goal]:
        """Update goal progress."""
        goal = await self.get_goal(goal_id, user_id)
        if not goal:
            return None

        goal.progress_percentage = min(100.0, max(0.0, progress_percentage))
        goal.updated_at = datetime.utcnow()

        if goal.progress_percentage == 100.0 and goal.status != GoalStatus.COMPLETED:
            goal.status = GoalStatus.COMPLETED
            goal.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(goal)

        return goal

    async def _create_embedding(self, goal: Goal) -> None:
        """Create embedding for goal (for RAG)."""
        content = f"Goal: {goal.title}\n\nDescription: {goal.description}"

        embedding_vector = await self.rag._generate_embedding(content)

        embedding = Embedding(
            id=str(uuid.uuid4()),
            user_id=goal.user_id,
            entity_type="goal",
            entity_id=goal.id,
            content=content,
            embedding=embedding_vector,
            model="text-embedding-3-small",
            metadata={
                "goal_status": goal.status.value,
                "goal_priority": goal.priority.value
            }
        )

        self.db.add(embedding)
        await self.db.commit()

    async def _update_embedding(self, goal: Goal) -> None:
        """Update embedding when goal description changes."""
        # Delete old embedding
        await self.db.execute(
            delete(Embedding).where(
                Embedding.entity_type == "goal",
                Embedding.entity_id == goal.id
            )
        )

        # Create new embedding
        await self._create_embedding(goal)
