from typing import Protocol, Any

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
import redis.asyncio as redis
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue


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


class RabbitMQManagerProtocol(Protocol):

    @property
    def is_connected(self) -> bool:
        ...

    @property
    def channel(self) -> AbstractChannel | None:
        ...

    @property
    def validation_queue(self) -> AbstractQueue | None:
        ...

    @property
    def result_queue(self) -> AbstractQueue | None:
        ...

    async def connect(self) -> None:
        ...

    async def close(self) -> None:
        ...

    async def publish_validation_request(
        self,
        user_id: int,
        permission_type: str,
        item_id: int,
        request_id: str,
    ) -> None:
        ...

