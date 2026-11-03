from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import SecretStr

class Settings(BaseSettings):
    # Reads values from the .env file; ignores variables we don't declare
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    BOT_TOKEN: str
    WEBHOOK_SECRET: str | None = None
    GROQ_API_KEY: SecretStr 






@lru_cache  # build Settings once, reuse everywhere
def get_settings() -> Settings:
    return Settings() # type: ignore