from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Reads values from the .env file; ignores variables we don't declare
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    WHATSAPP_TOKEN: str
    WHATSAPP_PHONE_ID: str
    WHATSAPP_WEBHOOK_SECRET: str

    GROQ_API_KEY: SecretStr


@lru_cache  # build Settings once, reuse everywhere
def get_settings() -> Settings:
    return Settings()  # type: ignore
