from __future__ import annotations

import asyncio
from functools import lru_cache
from typing import AsyncGenerator, cast, Any

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from access_control_service.config.settings import Settings, get_settings
from access_control_service.db.database import Database
from access_control_service.services.redis_client import RedisClient
from access_control_service.db.protocols import DatabaseProtocol, RedisClientProtocol
from access_control_service.services.protocols import (
    ResourceServiceProtocol,
    AccessServiceProtocol,
    AccessServiceAdminProtocol,
    GroupServiceProtocol,
    ConflictServiceProtocol,
    ConflictServiceAdminProtocol,
)
from access_control_service.services.resource_service import ResourceService
from access_control_service.services.access_service import AccessService
from access_control_service.services.access_service_admin import AccessServiceAdmin
from access_control_service.services.group_service import GroupService
from access_control_service.services.conflict_service import ConflictService
from access_control_service.services.conflict_service_admin import ConflictServiceAdmin


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


async def get_redis_connection() -> AsyncGenerator[redis.Redis[Any], None]:
    redis_client = get_redis_client()
    connection = redis_client.connection
    yield connection


def get_resource_service(
    session: AsyncSession = Depends(get_db_session),
) -> ResourceServiceProtocol:
    return ResourceService(session=session)


def get_access_service(
    session: AsyncSession = Depends(get_db_session),
) -> AccessServiceProtocol:
    return AccessService(session=session)


def get_access_service_admin(
    session: AsyncSession = Depends(get_db_session),
) -> AccessServiceAdminProtocol:
    return AccessServiceAdmin(session=session)


def get_group_service(
    session: AsyncSession = Depends(get_db_session),
) -> GroupServiceProtocol:
    return GroupService(session=session)


def get_conflict_service(
    session: AsyncSession = Depends(get_db_session),
) -> ConflictServiceProtocol:
    return ConflictService(session=session)


def get_conflict_service_admin(
    session: AsyncSession = Depends(get_db_session),
) -> ConflictServiceAdminProtocol:
    return ConflictServiceAdmin(session=session)

