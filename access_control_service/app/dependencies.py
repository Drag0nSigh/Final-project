from __future__ import annotations

from functools import lru_cache
from typing import AsyncGenerator

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.config.settings import Settings, get_settings
from access_control_service.db.database import Database
from access_control_service.services.redis_client import RedisClient
from access_control_service.db.protocols import DatabaseProtocol, RedisClientProtocol


@lru_cache(maxsize=1)
def get_settings_dependency() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_database() -> DatabaseProtocol:
    return Database()


@lru_cache(maxsize=1)
def get_redis_client() -> RedisClientProtocol:
    return RedisClient()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db = get_database()
    async for session in db.get_db():
        yield session


async def get_redis_connection() -> AsyncGenerator[redis.Redis, None]:
    redis_client = get_redis_client()
    connection = redis_client.connection
    yield connection

