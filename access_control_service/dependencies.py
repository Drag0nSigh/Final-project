from __future__ import annotations

import asyncio
from functools import lru_cache
from typing import AsyncGenerator, cast

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


_db_connect_lock: asyncio.Lock | None = None


def _get_db_connect_lock() -> asyncio.Lock:
    global _db_connect_lock
    if _db_connect_lock is None:
        _db_connect_lock = asyncio.Lock()
    return _db_connect_lock


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    db = cast(Database, get_database())
    
    if db.AsyncSessionLocal is None:
        async with _get_db_connect_lock():
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

