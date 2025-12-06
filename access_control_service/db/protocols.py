from typing import Protocol, Any

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
import redis.asyncio as redis


class DatabaseProtocol(Protocol):

    engine: AsyncEngine | None
    AsyncSessionLocal: async_sessionmaker | None

    async def connect(self) -> None:
        ...

    async def init_db(self) -> None:
        ...

    async def close(self) -> None:
        ...


class RedisClientProtocol(Protocol):

    @property
    def connection(self) -> redis.Redis[Any]:
        ...

    async def connect(self) -> None:
        ...

    async def close(self) -> None:
        ...

