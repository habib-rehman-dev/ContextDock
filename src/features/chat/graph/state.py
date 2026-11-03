# app/features/chat/graph/state.py
from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel


class ChatAgentState(BaseModel):
    # 'add_messages' appends new entries to existing message list
    messages: Annotated[list[BaseMessage], add_messages]
    chat_id: int
    user_intent: str | None = "general_chat"
