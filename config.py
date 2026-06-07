from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field, field_validator
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
        extra="ignore"
    )

    @field_validator('admin_ids', mode='before')
    @classmethod
    def parse_admin_ids(cls, v):
        """String'dan list'ga o'girib berish"""
        if isinstance(v, str):
            # "6038831784" yoki "123,456,789" formasini o'qish
            return [int(x.strip()) for x in v.split(',') if x.strip().isdigit()]
        if isinstance(v, list):
            return v
        if isinstance(v, int):
            return [v]
        return []

config = Settings()
