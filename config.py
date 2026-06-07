from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import List

class Settings(BaseSettings):
    """
    Bot va boshqa xizmatlar uchun sozlamalar (Environment variables).
    """
    bot_token: SecretStr
    openrouter_api_key: SecretStr
    openai_api_key: SecretStr
    database_url: str
    admin_ids: List[int]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

config = Settings()
