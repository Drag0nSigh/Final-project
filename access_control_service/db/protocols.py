from typing import Protocol, AsyncGenerator, Any

from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis


class DatabaseProtocol(Protocol):

    async def connect(self) -> None:
        ...

    async def init_db(self) -> None:
        ...

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
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

