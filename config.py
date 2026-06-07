from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field
from typing import List, Optional

class Settings(BaseSettings):
    """
    Bot va boshqa xizmatlar uchun sozlamalar (Environment variables).
    """
    bot_token: SecretStr
    openrouter_api_key: Optional[SecretStr] = None
    openai_api_key: Optional[SecretStr] = None
    database_url: str
    admin_ids: List[int] = Field(default_factory=list)
    google_api_key: Optional[SecretStr] = None
    webapp_url: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Qo'shimcha o'zgaruvchilarni e'tibor bermang
    )

config = Settings()
