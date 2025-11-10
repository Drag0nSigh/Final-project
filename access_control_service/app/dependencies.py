from __future__ import annotations

from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends

from access_control_service.config.settings import Settings, get_settings
from access_control_service.services.redis_client import redis_client


def get_settings_dependency() -> Settings:
    """Возвращает singleton-настройки Access Control Service."""

    return get_settings()


async def get_redis_connection() -> AsyncGenerator[redis.Redis, None]:
    """Даёт активное соединение с Redis для использования в эндпоинтах."""
    connection = redis_client.connection
    yield connection

