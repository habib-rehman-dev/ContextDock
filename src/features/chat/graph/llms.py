from langchain_groq import ChatGroq

# impor settings from core.config
from src.core.config import get_settings

settings = get_settings()


groq = ChatGroq(
    model="qwen/qwen3.8-27b",
    api_key=settings.GROQ_API_KEY,
    temperature=0.7,
    max_tokens=500,
)
