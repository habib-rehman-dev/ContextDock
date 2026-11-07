# state.py (new, minimal)
from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel


class SimpleChatState(BaseModel):
    # add_messages is a reducer: when a node returns {"messages": [...]},
    # the new messages are APPENDED to history instead of replacing it
    messages: Annotated[list[BaseMessage], add_messages]
