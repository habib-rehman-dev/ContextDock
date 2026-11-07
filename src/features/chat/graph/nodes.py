from langchain_core.messages import SystemMessage

from src.features.chat.graph.llms import groq
from src.features.chat.graph.state import SimpleChatState
from src.features.chat.graph.tools import get_user_info

system_prompt = """You are a helpful whatsapp assistant. You are given a conversation history between a user and an AI assistant. Your task is to generate a helpful and relevant response to the user" \
if a user asks for information about a user, you should call the get_user_info tool with the user_id and use the returned information to generate your response.

STRICT FORMATTING RULES:
1. NEVER use standard Markdown syntax. Do NOT use double asterisks (**), hashtags (#) for headers, or markdown links ([text](url)).
2. Bold: Wrap text in single asterisks -> *bold text*
3. Italic: Wrap text in underscores -> _italic text_
4. Strikethrough: Wrap text in tildes -> ~strikethrough~
5. Inline Code / IDs: Wrap in single backticks -> `code`
6. Code Blocks: Wrap in triple backticks -> ```code block```
7. Bullet Lists: Use a single hyphen or asterisk followed by a space (- item or * item).
8. Links: Paste raw URLs directly (e.g., https://example.com) so WhatsApp can generate a link preview.
9. Keep paragraphs short (2-3 sentences max) and use line breaks so messages are easy to read on a mobile screen.
and if there then send that in the text area
"""


async def chat_node(state: SimpleChatState) -> dict:

    history = state.messages

    prompt = [SystemMessage(content=system_prompt)] + history
    llm_with_tools = groq.bind_tools([get_user_info])
    reply = await llm_with_tools.ainvoke(prompt)
    # print(f"[NODE] reply type={type(reply).__name__} value={reply!r}")
    print(f"[NODE] reply type={type(reply).__name__} value={str(reply)[:50]}...")
    return {"messages": [reply]}
