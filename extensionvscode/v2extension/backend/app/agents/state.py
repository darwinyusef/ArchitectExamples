"""LangGraph state definition."""

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State shared across all agent nodes."""

    # User context
    user_id: str
    goal_id: str | None
    task_id: str | None

    # Messages
    messages: Annotated[Sequence[BaseMessage], "Chat messages"]

    # Execution context
    current_node: str
    next_node: str | None

    # User data
    code_snapshot: str | None
    validation_results: dict | None

    # Agent-specific data
    mood_score: float  # Nodo 8
    performance_metrics: dict | None  # Nodo 5
    contract_status: str | None  # Nodo 9
    context_priority: list[str] | None  # Nodo 7

    # Flags
    is_authenticated: bool
    needs_motivation: bool
    state_change_required: bool
