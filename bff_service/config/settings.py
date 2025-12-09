from functools import lru_cache

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    user_service_url: AnyUrl = Field(
        default="http://user-service:8000",
        description="URL User Service",
    )
    access_control_service_url: AnyUrl = Field(
        default="http://access-control-service:8000",
        description="URL Access Control Service",
    )

    http_timeout: float = Field(
        default=30.0,
        description="Таймаут для HTTP запросов (секунды)",
    )

    log_level: str = Field(
        default="INFO",
        description="Уровень логирования",
    )

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

