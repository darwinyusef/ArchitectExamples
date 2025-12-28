"""
Task Tools for LangGraph agents.

These tools allow agents to create, update, and validate tasks.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Task, TaskStatus, TaskType, CodeSnapshot
from app.agents.tools.rag_tools import get_similar_code, RAGTools


async def create_task_tool(
    user_id: str,
    goal_id: str,
    title: str,
    description: str,
    task_type: str = "code",
    priority: int = 100,
    estimated_hours: Optional[float] = None
) -> Dict[str, Any]:
    """
    Create a new task.

    Args:
        user_id: User ID
        goal_id: Parent goal ID
        title: Task title
        description: Task description
        task_type: code, documentation, testing, research, review, deployment, other
        priority: Priority number (lower = higher priority)
        estimated_hours: Estimated hours to complete

    Returns:
        Created task info
    """
    task_id = str(uuid.uuid4())

    async with AsyncSessionLocal() as db:
        task = Task(
            id=task_id,
            goal_id=goal_id,
            user_id=user_id,
            title=title,
            description=description,
            task_type=TaskType[task_type.upper()],
            status=TaskStatus.TODO,
            priority=priority,
            estimated_hours=estimated_hours
        )

        db.add(task)
        await db.commit()
        await db.refresh(task)

        # Generate embedding
        if description:
            rag = RAGTools()
            from app.models import Embedding

            embedding_vector = await rag._generate_embedding(
                f"{title}\n\n{description}"
            )

            embedding = Embedding(
                id=str(uuid.uuid4()),
                user_id=user_id,
                entity_type="task",
                entity_id=task_id,
                content=f"Task: {title}\n\nDescription: {description}",
                embedding=embedding_vector,
                model="text-embedding-3-small",
                metadata={
                    "task_type": task.task_type.value,
                    "task_status": task.status.value
                }
            )

            db.add(embedding)
            await db.commit()

        return {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "task_type": task.task_type.value,
            "status": task.status.value,
            "priority": task.priority,
            "created_at": task.created_at.isoformat()
        }


async def update_task_tool(
    task_id: str,
    user_id: str,
    status: Optional[str] = None,
    validation_result: Optional[Dict[str, Any]] = None,
    ai_feedback: Optional[str] = None,
    actual_hours: Optional[float] = None
) -> Dict[str, Any]:
    """
    Update task status and validation results.

    Args:
        task_id: Task ID
        user_id: User ID
        status: New status
        validation_result: Validation result from AI
        ai_feedback: AI feedback text
        actual_hours: Actual hours spent

    Returns:
        Updated task info
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id
            )
        )
        task = result.scalar_one_or_none()

        if not task:
            return {"error": "Task not found"}

        if status:
            task.status = TaskStatus[status.upper()]

            if status == "in_progress" and not task.started_at:
                task.started_at = datetime.utcnow()
            elif status == "completed" and not task.completed_at:
                task.completed_at = datetime.utcnow()

        if validation_result:
            task.validation_result = validation_result

        if ai_feedback:
            task.ai_feedback = ai_feedback

        if actual_hours is not None:
            task.actual_hours = actual_hours

        task.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(task)

        return {
            "task_id": task.id,
            "status": task.status.value,
            "validation_result": task.validation_result,
            "updated_at": task.updated_at.isoformat()
        }


async def validate_code_tool(
    user_id: str,
    task_id: str,
    code: str,
    file_path: str,
    language: str,
    use_rag: bool = True
) -> Dict[str, Any]:
    """
    Validate code using RAG to find similar validated code.

    This tool:
    1. Searches for similar code that was previously validated
    2. Uses that context to provide better feedback
    3. Stores the code snapshot

    Args:
        user_id: User ID
        task_id: Task ID
        code: Code to validate
        file_path: Path to file
        language: Programming language
        use_rag: Use RAG for context

    Returns:
        Validation results with RAG context
    """
    # Search for similar validated code
    similar_code = []
    rag_context = None

    if use_rag:
        similar_code = await get_similar_code(
            code=code,
            user_id=user_id,
            language=language,
            limit=3,
            only_validated=True
        )

        rag_context = {
            "similar_code_count": len(similar_code),
            "examples": [
                {
                    "file_path": c["file_path"],
                    "validation_score": c["validation_score"],
                    "similarity": c["similarity"],
                    "feedback_summary": c["validation_feedback"][:200] if c["validation_feedback"] else None
                }
                for c in similar_code
            ]
        }

    # Create code snapshot
    snapshot_id = str(uuid.uuid4())

    async with AsyncSessionLocal() as db:
        snapshot = CodeSnapshot(
            id=snapshot_id,
            task_id=task_id,
            user_id=user_id,
            file_path=file_path,
            language=language,
            code_content=code,
            metadata={
                "rag_context": rag_context,
                "validation_requested_at": datetime.utcnow().isoformat()
            }
        )

        db.add(snapshot)
        await db.commit()

        # TODO: Here you would call the actual AI validation
        # For now, return structure for agent to fill

        return {
            "snapshot_id": snapshot_id,
            "language": language,
            "file_path": file_path,
            "rag_context": rag_context,
            "similar_code_examples": [
                {
                    "code_snippet": c["code_content"][:500],
                    "feedback": c["validation_feedback"],
                    "score": c["validation_score"]
                }
                for c in similar_code[:2]  # Top 2
            ],
            "status": "pending_validation"
        }


async def list_tasks_tool(
    user_id: str,
    goal_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    List tasks for a user.

    Args:
        user_id: User ID
        goal_id: Optional goal filter
        status: Optional status filter
        limit: Max results

    Returns:
        List of tasks
    """
    async with AsyncSessionLocal() as db:
        query = select(Task).where(Task.user_id == user_id)

        if goal_id:
            query = query.where(Task.goal_id == goal_id)

        if status:
            query = query.where(Task.status == TaskStatus[status.upper()])

        query = query.order_by(Task.priority, Task.created_at.desc()).limit(limit)

        result = await db.execute(query)
        tasks = result.scalars().all()

        return [
            {
                "task_id": task.id,
                "goal_id": task.goal_id,
                "title": task.title,
                "description": task.description,
                "task_type": task.task_type.value,
                "status": task.status.value,
                "priority": task.priority,
                "validation_result": task.validation_result,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ]
