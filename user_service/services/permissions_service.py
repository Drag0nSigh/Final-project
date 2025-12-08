
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from datetime import datetime
from uuid import uuid4

import redis.asyncio as redis

from user_service.db.userpermission import UserPermission
from user_service.models.enums import PermissionType, PermissionStatus
from user_service.repositories.protocols import UserPermissionRepositoryProtocol

logger = logging.getLogger(__name__)
from user_service.services.cache import (
    invalidate_user_groups_cache,
    get_user_groups_from_cache,
    set_user_groups_cache,
)
from user_service.services.dto import (
    permission_model_to_schema,
    permissions_to_active_groups_schema,
)
from user_service.models.models import (
    RequestAccessRequest,
    RequestAccessResponse,
    GetUserPermissionsResponse,
    GetActiveGroupsResponse,
    ActiveGroup,
)


@dataclass
class PermissionService:

    permission_repository: UserPermissionRepositoryProtocol
    redis_conn: redis.Redis | None = None

    async def create_request(
        self,
        request_data: RequestAccessRequest,
    ) -> RequestAccessResponse:
        
        logger.debug(
            f"Создание заявки: user={request_data.user_id} "
            f"permission_type={request_data.permission_type} item_id={request_data.item_id}"
        )
        
        existing_permission = await self.permission_repository.find_by_user_id_and_permission_type(
            user_id=request_data.user_id,
            permission_type=request_data.permission_type.value,
            item_id=request_data.item_id,
        )
        
        if existing_permission and existing_permission.status in {PermissionStatus.ACTIVE.value, PermissionStatus.PENDING.value}:
            raise ValueError("Заявка уже находится в обработке или право активно")
        
        new_request_id = str(uuid4())
        
        if existing_permission and existing_permission.status in {PermissionStatus.REVOKED.value, PermissionStatus.REJECTED.value}:
            existing_permission.status = PermissionStatus.PENDING.value
            existing_permission.request_id = new_request_id
            existing_permission.assigned_at = None
            await self.permission_repository.save(existing_permission)
            logger.debug(
                f"Повторное использование заявки {new_request_id}: статус переведён в pending"
            )
        else:
            permission_record = UserPermission(
                user_id=request_data.user_id,
                permission_type=request_data.permission_type.value,
                item_id=request_data.item_id,
                item_name=None,
                status=PermissionStatus.PENDING.value,
                request_id=new_request_id,
                assigned_at=None,
            )
            await self.permission_repository.save(permission_record)
            logger.debug(f"Создана новая заявка {new_request_id}")
        
        logger.debug(f"Заявка {new_request_id} успешно создана")
        return RequestAccessResponse(status="accepted", request_id=new_request_id)

    async def get_permissions(self, user_id: int) -> GetUserPermissionsResponse:

        permissions = await self.permission_repository.find_by_user_id(user_id)

        groups = [
            permission_model_to_schema(permission)
            for permission in permissions
            if permission.permission_type == PermissionType.GROUP.value
        ]
        accesses = [
            permission_model_to_schema(permission)
            for permission in permissions
            if permission.permission_type != PermissionType.GROUP.value
        ]

        return GetUserPermissionsResponse(
            user_id=user_id,
            groups=groups,
            accesses=accesses,
        )

    async def get_active_groups(self, user_id: int) -> GetActiveGroupsResponse:

        if self.redis_conn is not None:
            cached = await get_user_groups_from_cache(self.redis_conn, user_id)
            if cached is not None:
                return GetActiveGroupsResponse(groups=[ActiveGroup(**item) for item in cached])

        permissions = await self.permission_repository.find_active_groups_by_user_id(user_id)
        response = permissions_to_active_groups_schema(permissions)

        if self.redis_conn is not None:
            await set_user_groups_cache(
                self.redis_conn,
                user_id,
                [group.model_dump() for group in response.groups],
            )

        return response

    async def apply_validation_result(
        self,
        request_id: str,
        approved: bool,
        user_id: int,
        permission_type: PermissionType,
        item_id: int,
    ) -> UserPermission | None:

        permission = await self.permission_repository.find_by_request_id(request_id)

        if permission is None:
            return None

        if (
            permission.user_id != user_id
            or permission.permission_type != permission_type.value
            or permission.item_id != item_id
        ):
            logger.warning(
                f"Несоответствие параметров заявки: request_id={request_id}, "
                f"ожидалось user_id={user_id}, permission_type={permission_type}, item_id={item_id}, "
                f"найдено user_id={permission.user_id}, permission_type={permission.permission_type}, item_id={permission.item_id}"
            )
            return None

        if approved:
            permission.status = PermissionStatus.ACTIVE.value
            permission.assigned_at = datetime.utcnow()
        else:
            permission.status = PermissionStatus.REJECTED.value

        await self.permission_repository.save(permission)

        if self.redis_conn is not None and permission_type.value == PermissionType.GROUP.value:
            await invalidate_user_groups_cache(self.redis_conn, user_id)
            logger.debug(
                f"Кэш активных групп инвалидирован: user_id={user_id} (из-за изменения статуса заявки {request_id})"
            )

        return permission

    async def revoke_permission(
        self,
        user_id: int,
        permission_type: PermissionType,
        item_id: int,
    ) -> UserPermission | None:

        permission = await self.permission_repository.find_by_user_id_and_type_and_item_and_status(
            user_id=user_id,
            permission_type=permission_type.value,
            item_id=item_id,
            statuses=[PermissionStatus.ACTIVE.value, PermissionStatus.PENDING.value],
        )

        if permission is None:
            return None

        permission.status = PermissionStatus.REVOKED.value
        permission.assigned_at = datetime.utcnow()
        await self.permission_repository.save(permission)

        if self.redis_conn is not None and permission.permission_type == PermissionType.GROUP.value:
            await invalidate_user_groups_cache(self.redis_conn, user_id)
            logger.debug(
                f"Кэш активных групп инвалидирован: user_id={user_id} (из-за отзыва группы permission_type={permission.permission_type}, item_id={permission.item_id})"
            )

        return permission
