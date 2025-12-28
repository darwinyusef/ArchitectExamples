"""LangGraph state machine definition with 9 agents."""

from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.agents.nodes import (
    auth_node,
    goal_generator_node,
    course_manager_node,
    feedback_node,
    performance_evaluator_node,
    state_monitor_node,
    context_organizer_node,
    emotional_support_node,
    contract_validator_node,
)


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


def create_agent_graph() -> StateGraph:
    """
    Create the LangGraph state machine with all 9 agent nodes.

    Returns:
        Configured StateGraph ready for compilation
    """
    # Create graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("nodo_1_auth", auth_node)
    graph.add_node("nodo_2_goal_generator", goal_generator_node)
    graph.add_node("nodo_3_course_manager", course_manager_node)
    graph.add_node("nodo_4_feedback", feedback_node)
    graph.add_node("nodo_5_performance", performance_evaluator_node)
    graph.add_node("nodo_6_state_monitor", state_monitor_node)
    graph.add_node("nodo_7_context_organizer", context_organizer_node)
    graph.add_node("nodo_8_emotional_support", emotional_support_node)
    graph.add_node("nodo_9_contract_validator", contract_validator_node)

    # Define edges (workflow transitions)

    # Entry point: always authenticate first
    graph.set_entry_point("nodo_1_auth")

    # Auth -> Context Organizer (understand user needs)
    graph.add_edge("nodo_1_auth", "nodo_7_context_organizer")

    # Context Organizer -> Goal Generator (create or continue goal)
    graph.add_edge("nodo_7_context_organizer", "nodo_2_goal_generator")

    # Goal Generator -> Course Manager (document goal)
    graph.add_edge("nodo_2_goal_generator", "nodo_3_course_manager")

    # Course Manager -> Feedback (start providing feedback)
    graph.add_edge("nodo_3_course_manager", "nodo_4_feedback")

    # Feedback has conditional edges based on state
    def should_evaluate_performance(state: AgentState) -> str:
        """Decide if performance evaluation is needed."""
        # Example: evaluate every 5 validations
        if state.get("validation_results"):
            return "nodo_5_performance"
        return "nodo_6_state_monitor"

    graph.add_conditional_edges(
        "nodo_4_feedback",
        should_evaluate_performance,
        {
            "nodo_5_performance": "nodo_5_performance",
            "nodo_6_state_monitor": "nodo_6_state_monitor",
        }
    )

    # Performance -> State Monitor
    graph.add_edge("nodo_5_performance", "nodo_6_state_monitor")

    # State Monitor -> check if state change needed
    def should_check_contract(state: AgentState) -> str:
        """Decide if contract validation is needed."""
        if state.get("state_change_required"):
            return "nodo_9_contract_validator"
        return "nodo_8_emotional_support"

    graph.add_conditional_edges(
        "nodo_6_state_monitor",
        should_check_contract,
        {
            "nodo_9_contract_validator": "nodo_9_contract_validator",
            "nodo_8_emotional_support": "nodo_8_emotional_support",
        }
    )

    # Contract Validator -> Emotional Support
    graph.add_edge("nodo_9_contract_validator", "nodo_8_emotional_support")

    # Emotional Support -> check if should continue or end
    def should_continue(state: AgentState) -> str:
        """Decide if workflow should continue or end."""
        next_node = state.get("next_node")
        if next_node:
            return next_node
        return END

    graph.add_conditional_edges(
        "nodo_8_emotional_support",
        should_continue,
        {
            "nodo_4_feedback": "nodo_4_feedback",  # Loop back for more feedback
            END: END,
        }
    )

    return graph


def compile_agent_graph(checkpointer=None) -> Any:
    """
    Compile the agent graph for execution.

    Args:
        checkpointer: Optional checkpoint saver (e.g., RedisSaver, MemorySaver)

    Returns:
        Compiled graph ready for invocation
    """
    graph = create_agent_graph()

    if checkpointer is None:
        checkpointer = MemorySaver()  # Use memory by default

    compiled = graph.compile(checkpointer=checkpointer)

    return compiled
