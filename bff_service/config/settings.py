from functools import lru_cache
from typing import Final

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурационные параметры BFF Service."""

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
        env_prefix="BFF_SERVICE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


ENV_FILE_ENV_VAR: Final[str] = "BFF_SERVICE_ENV_FILE"


@lru_cache(maxsize=1)
def get_settings(env_file: str | None = None) -> Settings:
    """Возвращает singleton-экземпляр настроек."""

    if env_file is None:
        import os

        env_file = os.getenv(ENV_FILE_ENV_VAR)

    return Settings(_env_file=env_file)

