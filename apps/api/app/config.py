from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    elevenlabs_api_key: str = ""
    elevenlabs_model_id: str = "scribe_v2"
    elevenlabs_base_url: str = "https://api.elevenlabs.io"
    openai_api_key: str = ""
    openai_model_id: str = "gpt-6-astra"
    max_upload_mb: int = Field(default=100, ge=1, le=2000)
    request_timeout_seconds: float = Field(default=600, gt=0)
    frontend_origin: str = "http://localhost:3000"
    database_url: str = (
        "postgresql+psycopg://convoweave:convoweave@postgres:5432/convoweave"
    )
    media_root: str = "/data/media"

    @field_validator("database_url", mode="before")
    @classmethod
    def use_psycopg_driver(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
