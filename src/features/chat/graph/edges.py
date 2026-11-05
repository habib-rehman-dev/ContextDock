# app/features/chat/graph/edges.py
from src.features.chat.graph.state import ChatAgentState


def route_by_intent(state: ChatAgentState) -> str:
    if state.user_intent == "cancelled":
        return "cancel_node"
    if state.user_intent == "support":
        return "approval_node"
    return "generate_response"