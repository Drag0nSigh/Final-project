from __future__ import annotations

import asyncio
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
    PermissionServiceProtocol,
)
from user_service.repositories.protocols import (
    UserRepositoryProtocol,
    UserPermissionRepositoryProtocol,
)
from user_service.repositories.user_repository import UserRepository
from user_service.repositories.user_permission_repository import UserPermissionRepository
from user_service.services.permissions_service import PermissionService
from fastapi import Depends


@lru_cache(maxsize=1)
def get_settings_dependency() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_database() -> DatabaseProtocol:
    return Database()


@lru_cache(maxsize=1)
def get_redis_client() -> RedisClientProtocol:
    return RedisClient()


_rabbitmq_manager: RabbitMQManagerProtocol | None = None


def get_rabbitmq_manager(
    settings: Settings | None = None,
) -> RabbitMQManagerProtocol:
    global _rabbitmq_manager
    if _rabbitmq_manager is None:
        if settings is None:
            settings = get_settings_dependency()
        _rabbitmq_manager = RabbitMQManager(settings=settings)
    return _rabbitmq_manager


def get_rabbitmq_manager_dependency(
    settings: Settings = Depends(get_settings_dependency),
) -> RabbitMQManagerProtocol:
    return get_rabbitmq_manager(settings=settings)


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


def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserRepositoryProtocol:
    return UserRepository(session=session)


def get_user_permission_repository(
    session: AsyncSession = Depends(get_db_session),
) -> UserPermissionRepositoryProtocol:
    return UserPermissionRepository(session=session)


def get_permission_service(
    permission_repository: UserPermissionRepositoryProtocol = Depends(get_user_permission_repository),
    redis_conn: redis.Redis = Depends(get_redis_connection),
) -> PermissionServiceProtocol:
    return PermissionService(permission_repository=permission_repository, redis_conn=redis_conn)


def create_permission_service(
    session: AsyncSession,
    redis_conn: redis.Redis | None = None,
) -> PermissionServiceProtocol:
    permission_repository = UserPermissionRepository(session=session)
    return PermissionService(permission_repository=permission_repository, redis_conn=redis_conn)
