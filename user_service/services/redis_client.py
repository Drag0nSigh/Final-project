from __future__ import annotations

from typing import Any, Optional

import redis.asyncio as redis

from user_service.config.settings import get_settings


class RedisClient:

    def __init__(self) -> None:
        self._settings = get_settings()
        self._connection: Optional[redis.Redis[Any]] = None

    @property
    def connection(self) -> redis.Redis[Any]:
        """Ленивая выдача текущего подключения."""

        if self._connection is None:
            raise RuntimeError(
                "RedisClient не инициализирован. Вызовите connect() в lifecycle приложения."
            )
        return self._connection

    async def connect(self) -> None:
        """Устанавливает асинхронное соединение с Redis, если его ещё нет"""

        if self._connection is not None:
            return

        dsn = self._settings.build_redis_dsn()
        self._connection = redis.from_url(dsn, decode_responses=True)

    async def close(self) -> None:
        """Закрывает соединение с Redis, если оно существует."""

        if self._connection is None:
            return

        await self._connection.close()
        self._connection = None


# Глобальный singleton, который будем импортировать в других частях кода.
redis_client = RedisClient()
