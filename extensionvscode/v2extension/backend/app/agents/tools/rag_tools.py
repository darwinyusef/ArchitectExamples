"""
RAG (Retrieval-Augmented Generation) Tools for LangGraph.

These tools enable agents to retrieve relevant context from the database
using semantic search with pgvector.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.openai_tracker import OpenAITracker
from app.models import Goal, Task, CodeSnapshot, Course, Embedding


class RAGTools:
    """RAG tools for semantic search and context retrieval."""

    def __init__(self):
        self.openai_tracker = OpenAITracker()

    async def _generate_embedding(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """
        Generate embedding vector for text with token tracking.

        Args:
            text: Text to embed
            model: OpenAI embedding model to use

        Returns:
            List of floats representing the embedding vector (1536 dims)
        """
        # Usa el tracker que registra automáticamente el uso de tokens
        return await self.openai_tracker.create_embedding(text, model)


async def get_similar_goals(
    query: str,
    user_id: str,
    limit: int = 5,
    min_similarity: float = 0.7,
    only_completed: bool = True,
    course_id: Optional[str] = None,
    scope: str = "user"
) -> List[Dict[str, Any]]:
    """
    Retrieve similar goals using semantic search (RAG).

    This tool helps agents learn from past successful goals to provide
    better suggestions and context.

    Args:
        query: Text query to search for (e.g., new goal description)
        user_id: User ID to filter by
        limit: Maximum number of results
        min_similarity: Minimum cosine similarity (0-1)
        only_completed: Only return completed goals
        course_id: Optional course ID to filter by
        scope: RAG scope - "user" (only user's data), "course" (all users in course), "global" (all data)

    Returns:
        List of dicts with goal info and similarity scores

    Example:
        >>> # RAG solo del usuario
        >>> similar = await get_similar_goals(
        ...     "Learn FastAPI and build REST API",
        ...     user_id="usr_123",
        ...     scope="user"
        ... )

        >>> # RAG de todos los usuarios en el mismo curso
        >>> similar = await get_similar_goals(
        ...     "Build authentication system",
        ...     user_id="usr_123",
        ...     course_id="course_456",
        ...     scope="course"
        ... )
    """
    rag = RAGTools()

    # 1. Generate embedding for query
    query_embedding = await rag._generate_embedding(query)

    # 2. Build dynamic filters based on scope
    async with AsyncSessionLocal() as db:
        # Use cosine distance operator (<=>)
        # Lower distance = higher similarity
        # Similarity = 1 - distance

        # Build scope filter
        scope_filter = ""
        if scope == "user":
            scope_filter = "AND e.user_id = :user_id"
        elif scope == "course" and course_id:
            scope_filter = "AND g.course_id = :course_id"
        # scope == "global" -> no filter, all users

        # Build course filter (for user scope with specific course)
        course_filter = ""
        if scope == "user" and course_id:
            course_filter = "AND g.course_id = :course_id"

        # Build status filter
        status_filter = "AND g.status = 'completed'" if only_completed else ""

        sql = text(f"""
            SELECT
                g.id,
                g.user_id,
                g.course_id,
                g.title,
                g.description,
                g.status,
                g.priority,
                g.progress_percentage,
                g.ai_generated,
                g.validation_criteria,
                g.metadata,
                g.created_at,
                g.completed_at,
                e.content,
                1 - (e.embedding <=> :embedding) as similarity
            FROM embeddings e
            JOIN goals g ON e.entity_id = g.id
            WHERE
                e.entity_type = 'goal'
                {scope_filter}
                {course_filter}
                AND (1 - (e.embedding <=> :embedding)) >= :min_similarity
                {status_filter}
            ORDER BY e.embedding <=> :embedding
            LIMIT :limit
        """)

        params = {
            "embedding": str(query_embedding),
            "min_similarity": min_similarity,
            "limit": limit
        }

        if scope == "user":
            params["user_id"] = user_id
        if course_id:
            params["course_id"] = course_id

        result = await db.execute(sql, params)

        rows = result.fetchall()

        return [
            {
                "goal_id": row[0],
                "user_id": row[1],
                "course_id": row[2],
                "title": row[3],
                "description": row[4],
                "status": row[5],
                "priority": row[6],
                "progress_percentage": row[7],
                "ai_generated": row[8],
                "validation_criteria": row[9],
                "metadata": row[10],
                "created_at": row[11].isoformat() if row[11] else None,
                "completed_at": row[12].isoformat() if row[12] else None,
                "content": row[13],
                "similarity": float(row[14])
            }
            for row in rows
        ]


async def get_similar_code(
    code: str,
    user_id: str,
    language: str,
    limit: int = 5,
    min_similarity: float = 0.75,
    only_validated: bool = True,
    course_id: Optional[str] = None,
    scope: str = "user"
) -> List[Dict[str, Any]]:
    """
    Find similar code snippets that have been validated.

    This helps agents provide feedback based on previously validated code.

    Args:
        code: Code to search for
        user_id: User ID
        language: Programming language (python, javascript, etc.)
        limit: Maximum results
        min_similarity: Minimum similarity threshold
        only_validated: Only return validated code
        course_id: Optional course ID to filter by
        scope: RAG scope - "user" (only user's code), "course" (all users in course), "global" (all code)

    Returns:
        List of similar code snapshots with validation info

    Example:
        >>> # Buscar en código del usuario
        >>> similar_code = await get_similar_code(
        ...     code="async def get_user(db, user_id): ...",
        ...     user_id="usr_123",
        ...     language="python",
        ...     scope="user"
        ... )

        >>> # Buscar en código de todo el curso (aprender de otros estudiantes)
        >>> similar_code = await get_similar_code(
        ...     code="def validate_email(email): ...",
        ...     user_id="usr_123",
        ...     language="python",
        ...     course_id="course_456",
        ...     scope="course"
        ... )
    """
    rag = RAGTools()

    # Generate embedding for code
    query_embedding = await rag._generate_embedding(code)

    async with AsyncSessionLocal() as db:
        # Build scope filter
        scope_filter = ""
        if scope == "user":
            scope_filter = "AND cs.user_id = :user_id"
        elif scope == "course" and course_id:
            # Find code from all users in the same course through tasks/goals
            scope_filter = """
                AND cs.task_id IN (
                    SELECT t.id FROM tasks t
                    JOIN goals g ON t.goal_id = g.id
                    WHERE g.course_id = :course_id
                )
            """

        # Build validation filter
        validation_filter = ""
        if only_validated:
            validation_filter = "AND cs.validation_passed = true AND cs.validation_score > 0.8"

        sql = text(f"""
            SELECT
                cs.id,
                cs.user_id,
                cs.task_id,
                cs.file_path,
                cs.language,
                cs.code_content,
                cs.validation_passed,
                cs.validation_score,
                cs.validation_feedback,
                cs.issues_found,
                cs.metadata,
                e.content,
                1 - (e.embedding <=> :embedding) as similarity
            FROM embeddings e
            JOIN code_snapshots cs ON e.entity_id = cs.id
            WHERE
                e.entity_type = 'code_snapshot'
                {scope_filter}
                AND cs.language = :language
                AND (1 - (e.embedding <=> :embedding)) >= :min_similarity
                {validation_filter}
            ORDER BY e.embedding <=> :embedding
            LIMIT :limit
        """)

        params = {
            "embedding": str(query_embedding),
            "language": language,
            "min_similarity": min_similarity,
            "limit": limit
        }

        if scope == "user":
            params["user_id"] = user_id
        if course_id:
            params["course_id"] = course_id

        result = await db.execute(sql, params)

        rows = result.fetchall()

        return [
            {
                "snapshot_id": row[0],
                "user_id": row[1],
                "task_id": row[2],
                "file_path": row[3],
                "language": row[4],
                "code_content": row[5],
                "validation_passed": row[6],
                "validation_score": float(row[7]) if row[7] else None,
                "validation_feedback": row[8],
                "issues_found": row[9],
                "metadata": row[10],
                "embedding_content": row[11],
                "similarity": float(row[12])
            }
            for row in rows
        ]


async def get_course_documentation(
    query: str,
    user_id: str,
    course_id: Optional[str] = None,
    limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant course documentation using semantic search.

    Args:
        query: What to search for
        user_id: User ID
        course_id: Optional specific course ID
        limit: Max results

    Returns:
        List of relevant course documentation chunks
    """
    rag = RAGTools()

    query_embedding = await rag._generate_embedding(query)

    async with AsyncSessionLocal() as db:
        sql = text("""
            SELECT
                c.id,
                c.title,
                c.description,
                c.status,
                c.metadata,
                e.content,
                1 - (e.embedding <=> :embedding) as similarity
            FROM embeddings e
            JOIN courses c ON e.entity_id = c.id
            WHERE
                e.entity_type = 'course'
                AND e.user_id = :user_id
                {course_filter}
            ORDER BY e.embedding <=> :embedding
            LIMIT :limit
        """.format(
            course_filter="AND c.id = :course_id" if course_id else ""
        ))

        params = {
            "embedding": str(query_embedding),
            "user_id": user_id,
            "limit": limit
        }
        if course_id:
            params["course_id"] = course_id

        result = await db.execute(sql, params)
        rows = result.fetchall()

        return [
            {
                "course_id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "metadata": row[4],
                "content": row[5],
                "similarity": float(row[6])
            }
            for row in rows
        ]


async def get_task_context(
    goal_id: str,
    user_id: str,
    include_completed: bool = True
) -> Dict[str, Any]:
    """
    Get full context for a goal including all tasks.

    This provides comprehensive context for agents working on goals.

    Args:
        goal_id: Goal ID
        user_id: User ID
        include_completed: Include completed tasks

    Returns:
        Dict with goal and all related tasks
    """
    async with AsyncSessionLocal() as db:
        # Get goal
        goal_result = await db.execute(
            select(Goal).where(
                Goal.id == goal_id,
                Goal.user_id == user_id
            )
        )
        goal = goal_result.scalar_one_or_none()

        if not goal:
            return {"error": "Goal not found"}

        # Get tasks
        task_query = select(Task).where(Task.goal_id == goal_id)
        if not include_completed:
            task_query = task_query.where(Task.status != "completed")

        task_result = await db.execute(task_query)
        tasks = task_result.scalars().all()

        return {
            "goal": {
                "id": goal.id,
                "title": goal.title,
                "description": goal.description,
                "status": goal.status.value,
                "priority": goal.priority.value,
                "progress_percentage": goal.progress_percentage,
                "validation_criteria": goal.validation_criteria,
                "metadata": goal.metadata,
            },
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "task_type": task.task_type.value,
                    "priority": task.priority,
                    "validation_result": task.validation_result,
                    "ai_feedback": task.ai_feedback,
                }
                for task in tasks
            ],
            "task_count": len(tasks),
            "completed_tasks": len([t for t in tasks if t.status.value == "completed"]),
        }


async def search_knowledge_base(
    query: str,
    user_id: str,
    entity_types: Optional[List[str]] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search across all entity types in the knowledge base.

    This is a general-purpose semantic search across goals, tasks, courses, and code.

    Args:
        query: Search query
        user_id: User ID
        entity_types: Optional list of entity types to search (e.g., ['goal', 'task'])
        limit: Max results

    Returns:
        List of results from all entity types
    """
    rag = RAGTools()

    query_embedding = await rag._generate_embedding(query)

    # Default to all entity types if not specified
    if not entity_types:
        entity_types = ['goal', 'task', 'course', 'code_snapshot']

    async with AsyncSessionLocal() as db:
        # Build dynamic query based on entity types
        entity_type_filter = "AND e.entity_type IN :entity_types" if entity_types else ""

        sql = text(f"""
            SELECT
                e.id,
                e.entity_type,
                e.entity_id,
                e.content,
                e.model,
                e.created_at,
                1 - (e.embedding <=> :embedding) as similarity
            FROM embeddings e
            WHERE
                e.user_id = :user_id
                {entity_type_filter}
            ORDER BY e.embedding <=> :embedding
            LIMIT :limit
        """)

        params = {
            "embedding": str(query_embedding),
            "user_id": user_id,
            "limit": limit
        }
        if entity_types:
            params["entity_types"] = tuple(entity_types)

        result = await db.execute(sql, params)
        rows = result.fetchall()

        return [
            {
                "embedding_id": row[0],
                "entity_type": row[1],
                "entity_id": row[2],
                "content": row[3],
                "model": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "similarity": float(row[6])
            }
            for row in rows
        ]


# Helper function to format RAG results for LLM prompts
def format_rag_context(results: List[Dict[str, Any]], max_results: int = 3) -> str:
    """
    Format RAG results into a text block for LLM context.

    Args:
        results: List of RAG results
        max_results: Maximum number of results to include

    Returns:
        Formatted string for LLM prompt
    """
    if not results:
        return "No relevant context found."

    context_parts = []
    for i, result in enumerate(results[:max_results], 1):
        similarity = result.get("similarity", 0)
        content = result.get("content", "")

        context_parts.append(
            f"[Context {i}] (similarity: {similarity:.2f})\n{content}\n"
        )

    return "\n".join(context_parts)
