# src/features/chat/graph/nodes.py

# from .workflow import compiled_graph
from langchain_core.messages import AIMessage
from langgraph.types import interrupt

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


async def approval_node(state: ChatAgentState) -> dict:
    """Pause and ask the user to confirm before generating a support answer."""
    # interrupt() surfaces this payload to the caller (services.py).
    decision = interrupt(
        {
            "question": "Do you want me to continue with a support answer? Reply 'yes' to proceed.",
            "user_text": str(state.messages[-1].content),
        }
    )

    # When resumed, `decision` is whatever we pass in Command(resume=...)
    approved = str(decision).strip().lower() in {"yes", "y", "true"}
    return {"user_intent": "support" if approved else "cancelled"}


async def handle_cancelled(state: ChatAgentState) -> dict:
    """Handle the case where the user cancels the support flow."""
    # You could also send a message back to the user here, if desired.
    return {"messages": AIMessage(content="Support flow cancelled.")}
