# src/features/chat/graph/nodes.py

# from .workflow import compiled_graph
from src.features.chat.graph.state import ChatAgentState

from .llms import groq


async def categorize_message(state: ChatAgentState) -> dict:
    """Node 1: Analyze user message intent."""
    last_message = str(state.messages[-1].content).lower()

    if "help" in last_message or "support" in last_message:
        intent = "support"
    else:
        intent = "general_chat"

    # Return state update dictionary
    return {"user_intent": intent}


async def generate_response(state: ChatAgentState) -> dict:
    """Node 2: Produce AI reply."""
    # intent = str(state.user_intent)
    # user_text = state.messages[-1].content

    messages = state.messages
    res = await groq.ainvoke(messages)
    # print(f"AI response: {res}")
    # reply = f"[{intent.upper()}] You said: '{user_text}'"
    return {"messages": res}
