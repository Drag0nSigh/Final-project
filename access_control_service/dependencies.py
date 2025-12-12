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
    ResourceServiceAdminProtocol,
    AccessServiceProtocol,
    AccessServiceAdminProtocol,
    GroupServiceProtocol,
    ConflictServiceProtocol,
    ConflictServiceAdminProtocol,
)
from access_control_service.services.resource_service import ResourceService
from access_control_service.services.resource_service_admin import ResourceServiceAdmin
from access_control_service.services.access_service import AccessService
from access_control_service.services.access_service_admin import AccessServiceAdmin
from access_control_service.services.group_service import GroupService
from access_control_service.services.conflict_service import ConflictService
from access_control_service.services.conflict_service_admin import ConflictServiceAdmin
from access_control_service.repositories.access_repository import AccessRepository
from access_control_service.repositories.resource_repository import ResourceRepository
from access_control_service.repositories.group_repository import GroupRepository
from access_control_service.repositories.conflict_repository import ConflictRepository
from access_control_service.repositories.protocols import (
    AccessRepositoryProtocol,
    ResourceRepositoryProtocol,
    GroupRepositoryProtocol,
    ConflictRepositoryProtocol,
)


@lru_cache(maxsize=1)
def get_settings_dependency() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_database() -> DatabaseProtocol:
    settings = get_settings_dependency()
    return Database(settings=settings)


@lru_cache(maxsize=1)
def get_redis_client() -> RedisClientProtocol:
    return RedisClient()


@lru_cache(maxsize=1)
def _get_db_connect_lock() -> asyncio.Lock:
    return asyncio.Lock()


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


def get_access_repository(
    session: AsyncSession = Depends(get_db_session),
) -> AccessRepositoryProtocol:
    return AccessRepository(session=session)


def get_resource_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ResourceRepositoryProtocol:
    return ResourceRepository(session=session)


def get_resource_service(
    resource_repository: ResourceRepositoryProtocol = Depends(get_resource_repository),
) -> ResourceServiceProtocol:
    return ResourceService(resource_repository=resource_repository)


def get_resource_service_admin(
    resource_repository: ResourceRepositoryProtocol = Depends(get_resource_repository),
) -> ResourceServiceAdminProtocol:
    return ResourceServiceAdmin(resource_repository=resource_repository)


def get_access_service(
    access_repository: AccessRepositoryProtocol = Depends(get_access_repository),
    resource_repository: ResourceRepositoryProtocol = Depends(get_resource_repository),
) -> AccessServiceProtocol:
    return AccessService(
        access_repository=access_repository,
        resource_repository=resource_repository,
    )


def get_access_service_admin(
    access_repository: AccessRepositoryProtocol = Depends(get_access_repository),
    resource_repository: ResourceRepositoryProtocol = Depends(get_resource_repository),
) -> AccessServiceAdminProtocol:
    return AccessServiceAdmin(
        access_repository=access_repository,
        resource_repository=resource_repository,
    )


def get_group_repository(
    session: AsyncSession = Depends(get_db_session),
) -> GroupRepositoryProtocol:
    return GroupRepository(session=session)


def get_conflict_repository(
    session: AsyncSession = Depends(get_db_session),
) -> ConflictRepositoryProtocol:
    return ConflictRepository(session=session)


def get_group_service(
    group_repository: GroupRepositoryProtocol = Depends(get_group_repository),
    access_repository: AccessRepositoryProtocol = Depends(get_access_repository),
    conflict_repository: ConflictRepositoryProtocol = Depends(get_conflict_repository),
) -> GroupServiceProtocol:
    return GroupService(
        group_repository=group_repository,
        access_repository=access_repository,
        conflict_repository=conflict_repository,
    )


def get_conflict_service(
    conflict_repository: ConflictRepositoryProtocol = Depends(get_conflict_repository),
) -> ConflictServiceProtocol:
    return ConflictService(conflict_repository=conflict_repository)


def get_conflict_service_admin(
    group_repository: GroupRepositoryProtocol = Depends(get_group_repository),
    conflict_repository: ConflictRepositoryProtocol = Depends(get_conflict_repository),
) -> ConflictServiceAdminProtocol:
    return ConflictServiceAdmin(
        group_repository=group_repository,
        conflict_repository=conflict_repository,
    )
