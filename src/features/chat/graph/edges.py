# app/features/chat/graph/edges.py
from src.features.chat.graph.state import ChatAgentState


def route_by_intent(state: ChatAgentState) -> str:
    """Conditional edge router function."""
    intent = state.user_intent

    if intent == "support":
        return "generate_response"
    return "generate_response"  # Route to specific node names based on logic
