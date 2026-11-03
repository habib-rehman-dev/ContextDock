from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from src.features.chat.graph.edges import route_by_intent
from src.features.chat.graph.nodes import categorize_message, generate_response
from src.features.chat.graph.state import ChatAgentState


def build_chat_graph():
    # 1. Initialize with State schema
    builder = StateGraph(ChatAgentState)

    # 2. Add Nodes
    builder.add_node("categorize_message", categorize_message)
    builder.add_node("generate_response", generate_response)

    # 3. Add Edges
    builder.add_edge(START, "categorize_message")

    # Conditional Edge: routes from 'categorize_message' dynamically
    builder.add_conditional_edges(
        "categorize_message",
        route_by_intent,
        {"generate_response": "generate_response"},
    )

    builder.add_edge("generate_response", END)

    # 4. Compile execution graph

    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)


compiled_graph = build_chat_graph()

