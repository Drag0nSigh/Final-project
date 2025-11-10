from __future__ import annotations

from typing import Iterable

from user_service.db.userpermission import UserPermission as UserPermissionModel
from user_service.models.models import (
    PermissionOut,
    ActiveGroup,
    GetActiveGroupsOut,
)


def permission_model_to_schema(permission: UserPermissionModel) -> PermissionOut:
    """Преобразует SQLAlchemy-модель ``UserPermission`` в ``PermissionOut``."""

    return PermissionOut(
        id=permission.id,
        permission_type=permission.permission_type,
        item_id=permission.item_id,
        item_name=permission.item_name,
        status=permission.status,
        assigned_at=permission.assigned_at,
    )


def permissions_to_active_groups_schema(
    permissions: Iterable[UserPermissionModel],
) -> GetActiveGroupsOut:
    """Формирует ответ ``GetActiveGroupsOut`` из набора ``UserPermission``."""

    groups: list[ActiveGroup] = []
    for permission in permissions:
        groups.append(
            ActiveGroup(
                id=permission.item_id,
                name=permission.item_name,
            )
        )

    return GetActiveGroupsOut(groups=groups)
