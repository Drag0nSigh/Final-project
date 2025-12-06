from __future__ import annotations

from functools import lru_cache
from typing import AsyncGenerator, cast

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.config.settings import Settings, get_settings
from user_service.db.database import Database
from user_service.services.redis_client import RedisClient
from user_service.services.rabbitmq_manager import RabbitMQManager
from user_service.db.protocols import (
    DatabaseProtocol,
    RedisClientProtocol,
    RabbitMQManagerProtocol,
)


@lru_cache(maxsize=1)
def get_settings_dependency() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_database() -> DatabaseProtocol:
    return Database()


@lru_cache(maxsize=1)
def get_redis_client() -> RedisClientProtocol:
    return RedisClient()


@lru_cache(maxsize=1)
def get_rabbitmq_manager() -> RabbitMQManagerProtocol:
    return RabbitMQManager()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db = cast(Database, get_database())
    
    if db.AsyncSessionLocal is None:
        await db.connect()
    
    async with db.AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_redis_connection() -> AsyncGenerator[redis.Redis, None]:
    redis_client = get_redis_client()
    connection = redis_client.connection
    yield connection
