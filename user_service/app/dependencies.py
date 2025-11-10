
from __future__ import annotations

from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends

from user_service.config.settings import Settings, get_settings
from user_service.services.redis_client import redis_client
from user_service.services.rabbitmq_manager import rabbitmq_manager, RabbitMQManager


def get_settings_dependency() -> Settings:
    """Возвращает singleton-настройки User Service."""

    return get_settings()


async def get_redis_connection() -> AsyncGenerator[redis.Redis, None]:
    """Даёт активное соединение с Redis."""

    connection = redis_client.connection
    try:
        yield connection
    finally:
        pass


def get_rabbitmq_manager_dependency() -> RabbitMQManager:
    """Возвращает singleton-менеджер RabbitMQ."""

    return rabbitmq_manager
