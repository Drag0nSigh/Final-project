
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal, Any
from datetime import datetime

import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.db.userpermission import UserPermission

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
    """Инкапсулирует бизнес-логику управления правами пользователя."""

    session: AsyncSession
    redis_conn: redis.Redis[Any] | None = None

    async def create_request(
        self,
        request_data: RequestAccessRequest,
    ) -> RequestAccessResponse:
        """Создание заявки на получение доступа или группы прав."""
        
        from uuid import uuid4
        
        logger.debug(
            f"Создание заявки: user={request_data.user_id} "
            f"permission_type={request_data.permission_type} item_id={request_data.item_id}"
        )
        
        stmt = select(UserPermission).where(
            UserPermission.user_id == request_data.user_id,
            UserPermission.permission_type == request_data.permission_type,
            UserPermission.item_id == request_data.item_id,
        )
        result = await self.session.execute(stmt)
        existing_permission = result.scalar_one_or_none()
        
        if existing_permission and existing_permission.status in {"active", "pending"}:
            raise ValueError("Заявка уже находится в обработке или право активно")
        
        new_request_id = str(uuid4())
        
        if existing_permission and existing_permission.status in {"revoked", "rejected"}:
            existing_permission.status = "pending"
            existing_permission.request_id = new_request_id
            existing_permission.assigned_at = None
            logger.debug(
                f"Повторное использование заявки {new_request_id}: статус переведён в pending"
            )
        else:
            permission_record = UserPermission(
                user_id=request_data.user_id,
                permission_type=request_data.permission_type,
                item_id=request_data.item_id,
                item_name=None,
                status="pending",
                request_id=new_request_id,
                assigned_at=None,
            )
            self.session.add(permission_record)
            logger.debug(f"Создана новая заявка {new_request_id}")
        
        await self.session.flush()
        
        logger.debug(f"Заявка {new_request_id} успешно создана")
        return RequestAccessResponse(status="accepted", request_id=new_request_id)

    async def get_permissions(self, user_id: int) -> GetUserPermissionsResponse:
        """Возвращает все права пользователя, разделяя их на группы и доступы."""

        stmt = select(UserPermission).where(UserPermission.user_id == user_id)
        result = await self.session.execute(stmt)
        permissions = result.scalars().all()

        groups = []
        accesses = []
        for permission in permissions:
            schema = permission_model_to_schema(permission)
            if permission.permission_type == "group":
                groups.append(schema)
            else:
                accesses.append(schema)

        return GetUserPermissionsResponse(
            user_id=user_id,
            groups=groups,
            accesses=accesses,
        )

    async def get_active_groups(self, user_id: int) -> GetActiveGroupsResponse:
        """Возвращает активные группы пользователя, используя кэш Redis."""

        if self.redis_conn is not None:
            cached = await get_user_groups_from_cache(self.redis_conn, user_id)
            if cached is not None:
                return GetActiveGroupsResponse(groups=[ActiveGroup(**item) for item in cached])

        stmt = select(UserPermission).where(
            UserPermission.user_id == user_id,
            UserPermission.permission_type == "group",
            UserPermission.status == "active",
        )
        result = await self.session.execute(stmt)
        permissions = result.scalars().all()
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
        permission_type: Literal["access", "group"],
        item_id: int,
    ) -> UserPermission | None:
        """Применяет результат валидации к заявке пользователя."""

        stmt = select(UserPermission).where(UserPermission.request_id == request_id)
        result = await self.session.execute(stmt)
        permission = result.scalar_one_or_none()

        if permission is None:
            return None

        if (
            permission.user_id != user_id
            or permission.permission_type != permission_type
            or permission.item_id != item_id
        ):
            logger.warning(
                f"Несоответствие параметров заявки: request_id={request_id}, "
                f"ожидалось user_id={user_id}, permission_type={permission_type}, item_id={item_id}, "
                f"найдено user_id={permission.user_id}, permission_type={permission.permission_type}, item_id={permission.item_id}"
            )
            return None

        if approved:
            permission.status = "active"
            permission.assigned_at = datetime.utcnow()
        else:
            permission.status = "rejected"

        if self.redis_conn is not None and permission_type == "group":
            await invalidate_user_groups_cache(self.redis_conn, user_id)
            logger.debug(
                f"Кэш активных групп инвалидирован: user_id={user_id} (из-за изменения статуса заявки {request_id})"
            )

        return permission

    async def revoke_permission(
        self,
        user_id: int,
        permission_type: Literal["access", "group"],
        item_id: int,
    ) -> UserPermission | None:
        """Переводит право пользователя в статус ``revoked`` и очищает кэш."""

        stmt = select(UserPermission).where(
            UserPermission.user_id == user_id,
            UserPermission.permission_type == permission_type,
            UserPermission.item_id == item_id,
            UserPermission.status.in_(["active", "pending"]),
        )
        result = await self.session.execute(stmt)
        permission = result.scalar_one_or_none()

        if permission is None:
            return None

        permission.status = "revoked"
        permission.assigned_at = datetime.utcnow()

        if self.redis_conn is not None and permission.permission_type == "group":
            await invalidate_user_groups_cache(self.redis_conn, user_id)
            logger.debug(
                f"Кэш активных групп инвалидирован: user_id={user_id} (из-за отзыва группы permission_type={permission.permission_type}, item_id={permission.item_id})"
            )

        return permission
