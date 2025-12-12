from typing import Protocol
from contextlib import AbstractAsyncContextManager

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
import redis.asyncio as redis
from aio_pika.abc import AbstractChannel, AbstractQueue

from user_service.models.models import (
    RequestAccessRequest,
    RequestAccessResponse,
    GetUserPermissionsResponse,
    GetActiveGroupsResponse,
)
from user_service.models.enums import PermissionType
from user_service.db.userpermission import UserPermission


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
    def connection(self) -> redis.Redis:
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
        permission_type: PermissionType,
        item_id: int,
        request_id: str,
    ) -> None:
        ...


class PermissionServiceProtocol(Protocol):

    async def create_request(
        self,
        request_data: RequestAccessRequest,
    ) -> RequestAccessResponse:
        ...

    async def get_permissions(self, user_id: int) -> GetUserPermissionsResponse:
        ...

    async def get_active_groups(self, user_id: int) -> GetActiveGroupsResponse:
        ...

    async def apply_validation_result(
        self,
        request_id: str,
        approved: bool,
        user_id: int,
        permission_type: PermissionType,
        item_id: int,
    ) -> UserPermission | None:
        ...

    async def revoke_permission(
        self,
        user_id: int,
        permission_type: PermissionType,
        item_id: int,
    ) -> UserPermission | None:
        ...


class PermissionServiceFactoryProtocol(Protocol):

    def create_with_session(
        self,
    ) -> AbstractAsyncContextManager[PermissionServiceProtocol]:
        ...

