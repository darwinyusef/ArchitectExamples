"""
LangGraph Tools for AI Goals Tracker V2.

Tools provide the capabilities that agents can use to interact with
the system, including RAG (Retrieval-Augmented Generation) for context.
"""

from app.agents.tools.rag_tools import (
    get_similar_goals,
    get_similar_code,
    get_course_documentation,
    get_task_context,
    search_knowledge_base,
)

from app.agents.tools.goal_tools import (
    create_goal_tool,
    update_goal_tool,
    list_goals_tool,
)

from app.agents.tools.task_tools import (
    create_task_tool,
    update_task_tool,
    validate_code_tool,
)

__all__ = [
    # RAG tools
    "get_similar_goals",
    "get_similar_code",
    "get_course_documentation",
    "get_task_context",
    "search_knowledge_base",

    # Goal tools
    "create_goal_tool",
    "update_goal_tool",
    "list_goals_tool",

    # Task tools
    "create_task_tool",
    "update_task_tool",
    "validate_code_tool",
]
