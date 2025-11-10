from functools import lru_cache
from typing import Final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Набор конфигурационных параметров Access Control Service."""

    # --- Настройки базы данных PostgreSQL ----------------------------------------
    db_host: str = Field(
        default="postgres",
    )
    db_port: int = Field(
        default=5432,
    )
    db_user: str = Field(
        default="postgres",
    )
    db_password: str = Field(
        default="postgres",
    )
    db_name: str = Field(
        default="access_control_service",
    )

    database_url: str | None = Field(
        default=None,
        description="Полный URL подключения к БД (если задан, переопределяет отдельные параметры)",
    )
    server_database_url: str | None = Field(
        default=None,
        description="Полный URL подключения к серверной БД postgres (для создания БД)",
    )

    # --- Настройки Redis ---------------------------------------------------------
    redis_host: str = Field(
        default="redis",
    )
    redis_port: int = Field(
        default=6379,
    )
    redis_db: int = Field(
        default=0,
    )
    redis_username: str | None = Field(
        default=None,
    )
    redis_password: str | None = Field(
        default=None,
    )

    # --- TTL для кэша Redis (в секундах) ----------------------------------------
    cache_ttl_conflicts_matrix_seconds: int = Field(
        default=600,
        description=(
            "Время жизни кэша матрицы конфликтов (10 минут). "
            "Матрица конфликтов кэшируется в ключе 'conflicts:matrix'."
        ),
    )
    cache_ttl_group_accesses_seconds: int = Field(
        default=600,
        description=(
            "Время жизни кэша доступов группы (10 минут). "
            "Ключ формата: 'group:{group_id}:accesses'."
        ),
    )
    cache_ttl_access_groups_seconds: int = Field(
        default=600,
        description=(
            "Время жизни кэша групп по доступу (10 минут). "
            "Ключ формата: 'access:{access_id}:groups'."
        ),
    )

    # --- Настройки логирования --------------------------------------------------
    log_level: str = Field(
        default="INFO",
        description="Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    model_config = SettingsConfigDict(
        env_prefix="ACCESS_CONTROL_SERVICE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def build_database_url(self) -> str:
        """Сконструировать основную строку подключения к PostgreSQL."""
        if self.database_url:
            return self.database_url

        return (
            "postgresql+asyncpg://"
            f"{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def build_server_database_url(self) -> str:
        """Формирует строку подключения к серверной БД PostgreSQL."""
        if self.server_database_url:
            return self.server_database_url

        return (
            "postgresql+asyncpg://"
            f"{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/postgres"
        )

    def build_redis_dsn(self) -> str:
        """Формирует DSN-строку Redis в формате redis://."""

        credentials = ""
        if self.redis_username and self.redis_password:
            credentials = f"{self.redis_username}:{self.redis_password}@"
        elif self.redis_password and not self.redis_username:
            credentials = f":{self.redis_password}@"

        return f"redis://{credentials}{self.redis_host}:{self.redis_port}/{self.redis_db}"


ENV_FILE_ENV_VAR: Final[str] = "ACCESS_CONTROL_SERVICE_ENV_FILE"


@lru_cache(maxsize=1)
def get_settings(env_file: str | None = None) -> Settings:
    """Возвращает singleton-экземпляр настроек Access Control Service."""
    if env_file is None:
        import os

        env_file = os.getenv(ENV_FILE_ENV_VAR)

    return Settings(_env_file=env_file)

