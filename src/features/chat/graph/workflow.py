from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import END, START, StateGraph

from src.features.chat.graph.edges import route_by_intent
from src.features.chat.graph.nodes import (
    approval_node,
    categorize_message,
    generate_response,
    handle_cancelled,
)
from src.features.chat.graph.state import ChatAgentState

# Holds the compiled graph once the app has started.
# It stays None until init_graph() is called from the lifespan.
_compiled_graph = None


def build_chat_graph(checkpointer: AsyncSqliteSaver):
    """Build and compile the graph using an already-open async checkpointer."""
    builder = StateGraph(ChatAgentState)

    # Nodes
    builder.add_node("categorize_message", categorize_message)
    builder.add_node("generate_response", generate_response)
    builder.add_node("approval_node", approval_node)
    builder.add_node("cancel_node", handle_cancelled)

    # Edges
    builder.add_edge(START, "categorize_message")
    builder.add_conditional_edges(
        "categorize_message",
        route_by_intent,
        {
            "approval_node": "approval_node",
            # "cancel_node": "cancel_node",
            "generate_response": "generate_response",
        },
    )
    # after approval → either generate or cancel
    builder.add_conditional_edges(
        "approval_node",
        lambda s: "cancel_node" if s.user_intent == "cancelled" else "generate_response",
        {"cancel_node": "cancel_node", "generate_response": "generate_response"},
    )
    builder.add_edge("generate_response", END)
    builder.add_edge("cancel_node", END)

    # The checkpointer is passed in, not created here
    return builder.compile(checkpointer=checkpointer)


def init_graph(checkpointer: AsyncSqliteSaver) -> None:
    """Called once at startup to store the compiled graph."""
    global _compiled_graph
    _compiled_graph = build_chat_graph(checkpointer)


# def get_graph():
#     """Use this everywhere instead of importing compiled_graph directly."""
#     if _compiled_graph is None:
#         raise RuntimeError("Graph not initialized. Is the lifespan running?")
#     return _compiled_graph


import asyncio

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

_compiled_graph = None
_lock = asyncio.Lock()  # prevents two requests from initializing at once


async def get_graph():
    """Creates the graph on first call (inside the running event loop), then reuses it."""
    global _compiled_graph
    if _compiled_graph is None:
        async with _lock:
            if _compiled_graph is None:  # re-check after acquiring the lock
                # aiosqlite connection is created here, inside async code
                conn = await aiosqlite.connect("chat_graph_checkpoint.db")
                checkpointer = AsyncSqliteSaver(conn)
                await checkpointer.setup()  # creates tables if missing
                _compiled_graph = build_chat_graph(checkpointer)
    return _compiled_graph
