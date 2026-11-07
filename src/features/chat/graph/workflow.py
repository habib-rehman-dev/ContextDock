# workflow.py
import asyncio

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

# use the same "src." prefix everywhere so imports are consistent
from src.features.chat.graph.nodes import chat_node
from src.features.chat.graph.state import SimpleChatState
from src.features.chat.graph.tools import tools

# holds the compiled graph after the first call; None until then
_compiled_graph = None
# stops two simultaneous requests from building the graph twice
_lock = asyncio.Lock()


def build_chat_graph(checkpointer: AsyncSqliteSaver):
    """Build and compile the single-node graph with an open checkpointer."""
    builder = StateGraph(SimpleChatState)

    # the one and only node
    builder.add_node("chatagent", chat_node)
    builder.add_node("chat_tools", ToolNode(tools))

    # START -> chatagent -> END
    builder.add_edge(START, "chatagent")
    
    builder.add_conditional_edges(
        "chatagent",
        tools_condition,
        {"tools": "chat_tools", "__end__": "__end__"},
    )
    builder.add_edge("chat_tools", "chatagent")

    # the checkpointer is what gives each thread_id its own memory
    return builder.compile(checkpointer=checkpointer)


async def get_graph():
    """Create the graph on first call (inside the running event loop), then reuse it."""
    global _compiled_graph
    if _compiled_graph is None:
        async with _lock:
            if _compiled_graph is None:  # re-check after acquiring the lock
                conn = await aiosqlite.connect("chat_graph_checkpoint.db")
                checkpointer = AsyncSqliteSaver(conn)
                await checkpointer.setup()  # creates tables if missing
                _compiled_graph = build_chat_graph(checkpointer)
    return _compiled_graph
