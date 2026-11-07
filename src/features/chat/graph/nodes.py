from langchain_core.messages import SystemMessage

from src.features.chat.graph.llms import groq
from src.features.chat.graph.state import SimpleChatState

system_prompt = "You are a helpful whatsapp assistant. You are given a conversation history between a user and an AI assistant. Your task is to generate a helpful and relevant response to the user"


async def chat_node(state: SimpleChatState) -> dict:

    history = state.messages

    prompt = [SystemMessage(content='answer to every question')] + history

    reply = await groq.ainvoke(prompt)
    # print(f"[NODE] reply type={type(reply).__name__} value={reply!r}")
    print(f"[NODE] reply type={type(reply).__name__} value={str(reply)[:50]}...")
    text = reply.content if hasattr(reply, "content") else str(reply)
    return {"messages": [reply]}  
