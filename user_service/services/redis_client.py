from __future__ import annotations

import redis.asyncio as redis

from user_service.config.settings import get_settings


class RedisClient:

    def __init__(self) -> None:
        self._settings = get_settings()
        self._connection: redis.Redis | None = None

    @property
    def connection(self) -> redis.Redis:

        if self._connection is None:
            raise RuntimeError(
                "RedisClient не инициализирован. Вызовите connect() в lifecycle приложения."
            )
        return self._connection

    async def connect(self) -> None:

        if self._connection is not None:
            return

        dsn = self._settings.build_redis_dsn()
        self._connection = redis.from_url(dsn, decode_responses=True)

    async def close(self) -> None:

        if self._connection is None:
            return

        await self._connection.close()
        self._connection = None


redis_client = RedisClient()
