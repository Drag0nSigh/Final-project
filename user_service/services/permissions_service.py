
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal, Optional
from datetime import datetime

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
    GetUserPermissionsOut,
    GetActiveGroupsOut,
    ActiveGroup,
)


@dataclass
class PermissionService:
    """Инкапсулирует бизнес-логику управления правами пользователя."""

    session: AsyncSession
    redis_conn: Optional[object] = None  # redis.Redis[Any]; точный тип зададим позже

    async def create_request(self, *args, **kwargs):  # pragma: no cover - заглушка
        raise NotImplementedError

    async def get_permissions(self, user_id: int) -> GetUserPermissionsOut:
        """Возвращает все права пользователя, разделяя их на группы и доступы.

        ***ВАЖНО для BFF Service***: BFF использует этот метод для получения всех прав пользователя.
        Формат ответа: ``GetUserPermissionsOut`` с разделением на ``groups`` и ``accesses``.
        Каждый элемент содержит: id, permission_type, item_id, item_name, status, assigned_at.

        ***ВАЖНО для Access Control Service***: В будущем этот метод будет обогащаться данными из
        Access Control Service (детали доступов, ресурсы, вложенные структуры). BFF может агрегировать
        данные от User Service и Access Control Service для формирования полного ответа клиенту.

        Пока метод возвращает только данные из таблицы ``user_permissions`` без
        вложенных структур (доступы групп и т.п.). На следующем этапе добавим
        интеграцию с Access Control Service, чтобы обогащать ответ.
        """

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

        return GetUserPermissionsOut(
            user_id=user_id,
            groups=groups,
            accesses=accesses,
        )

    async def get_active_groups(self, user_id: int) -> GetActiveGroupsOut:
        """Возвращает активные группы пользователя, используя кэш Redis.

        ***ВАЖНО для Validation Service***: Validation Service использует этот метод для получения
        активных групп пользователя при проверке конфликтов. Формат ответа: ``GetActiveGroupsOut``
        с полем ``groups`` (list[ActiveGroup]), где каждый элемент содержит ``id`` (int) и ``name`` (Optional[str]).
        Возвращаются только группы со статусом ``active``. Используется кэш Redis для ускорения.
        """

        if self.redis_conn is not None:
            cached = await get_user_groups_from_cache(self.redis_conn, user_id)
            if cached is not None:
                return GetActiveGroupsOut(groups=[ActiveGroup(**item) for item in cached])

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
    ) -> Optional[UserPermission]:
        """Применяет результат валидации к заявке пользователя."""

        # Ищем заявку по request_id
        stmt = select(UserPermission).where(UserPermission.request_id == request_id)
        result = await self.session.execute(stmt)
        permission = result.scalar_one_or_none()

        if permission is None:
            return None

        if approved:
            permission.status = "active"
            permission.assigned_at = datetime.utcnow()
        else:
            permission.status = "rejected"

        if self.redis_conn is not None and permission_type == "group":
            await invalidate_user_groups_cache(self.redis_conn, user_id)
            logger.debug(
                "Кэш активных групп инвалидирован: user_id=%s (из-за изменения статуса заявки %s)",
                user_id,
                request_id,
            )

        return permission

    async def revoke_permission(
        self,
        user_id: int,
        permission_type: Literal["access", "group"],
        item_id: int,
    ) -> Optional[UserPermission]:
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
                "Кэш активных групп инвалидирован: user_id=%s (из-за отзыва группы permission_type=%s, item_id=%s)",
                user_id,
                permission_type,
                item_id,
            )

        return permission
