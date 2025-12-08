from typing import Any
from contextlib import asynccontextmanager
import logging

import redis.asyncio as redis

from user_service.db.protocols import (
    DatabaseProtocol,
    RedisClientProtocol,
    PermissionServiceProtocol,
)
from user_service.repositories.user_permission_repository import UserPermissionRepository
from user_service.services.permissions_service import PermissionService

logger = logging.getLogger(__name__)


class PermissionServiceFactory:

    def __init__(
        self,
        db: DatabaseProtocol,
        redis_client: RedisClientProtocol,
    ):
        self._db = db
        self._redis_client = redis_client

    @asynccontextmanager
    async def create_with_session(
        self,
    ):
        if self._db.AsyncSessionLocal is None:
            raise RuntimeError("БД не инициализирована")

        async with self._db.AsyncSessionLocal() as session:
            try:
                redis_conn = self._redis_client.connection
                
                permission_repository = UserPermissionRepository(session=session)
                service = PermissionService(
                    permission_repository=permission_repository,
                    redis_conn=redis_conn,
                )
                
                yield service
                await session.commit()
            except Exception:
                await session.rollback()
                raise

