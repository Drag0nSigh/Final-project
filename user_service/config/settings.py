from functools import lru_cache
from typing import Final

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Полный набор конфигурационных параметров User Service."""

    # --- Настройки базы данных -------------------------------------------------
    db_host: str = Field(
        default="postgres-user",
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
        default="user_service",
    )

    database_url: str | None = Field(
        default=None,
    )
    server_database_url: str | None = Field(
        default=None,
    )

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

    rabbitmq_host: str = Field(
        default="rabbitmq",
    )
    rabbitmq_port: int = Field(
        default=5672,
    )
    rabbitmq_user: str = Field(
        default="guest",
    )
    rabbitmq_password: str = Field(
        default="guest",
    )
    rabbitmq_virtual_host: str = Field(
        default="/",
    )
    rabbitmq_validation_queue: str = Field(
        default="validation_queue",
    )
    rabbitmq_result_queue: str = Field(
        default="result_queue",
    )

    access_control_service_url: AnyUrl = Field(
        default="http://access-control-service:8000",
    )
    validation_service_url: AnyUrl = Field(
        default="http://validation-service:8000",
    )
    bff_service_url: AnyUrl = Field(
        default="http://bff-service:8000",
    )

    cache_ttl_user_groups_seconds: int = Field(
        default=600,
        description=(
            "Время жизни кэша по активным группам пользователя (10 минут). "
        ),
    )

    log_level: str = Field(
        default="INFO",
    )

    model_config = SettingsConfigDict(
        env_prefix="USER_SERVICE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def build_database_url(self) -> str:
        """Сконструировать основную строку подключения к PostgreSQL."""

        return (
            self.database_url
            or "postgresql+asyncpg://"
            f"{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def build_server_database_url(self) -> str:
        """Формирует строку подключения к серверной БД."""

        return (
            self.server_database_url
            or "postgresql+asyncpg://"
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

    def build_rabbitmq_url(self) -> str:
        """Формирует URL для подключения к RabbitMQ (AMQP)."""

        return (
            "amqp://"
            f"{self.rabbitmq_user}:{self.rabbitmq_password}"
            f"@{self.rabbitmq_host}:{self.rabbitmq_port}{self.rabbitmq_virtual_host}"
        )


#: Название переменной окружения, откуда читается путь до .env файла.
ENV_FILE_ENV_VAR: Final[str] = "USER_SERVICE_ENV_FILE"


@lru_cache(maxsize=1)
def get_settings(env_file: str | None = None) -> Settings:
    """Возвращает singleton-экземпляр настроек."""

    if env_file is None:
        import os

        env_file = os.getenv(ENV_FILE_ENV_VAR)

    return Settings(_env_file=env_file)
