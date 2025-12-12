from __future__ import annotations

from typing import Iterable

from user_service.db.userpermission import UserPermission as UserPermissionModel
from user_service.models.models import (
    PermissionResponse,
    ActiveGroup,
    GetActiveGroupsResponse,
)


def permission_model_to_schema(permission: UserPermissionModel) -> PermissionResponse:

    return PermissionResponse(
        id=permission.id,
        permission_type=permission.permission_type,
        item_id=permission.item_id,
        item_name=permission.item_name,
        status=permission.status,
        assigned_at=permission.assigned_at,
    )


def permissions_to_active_groups_schema(
    permissions: Iterable[UserPermissionModel],
) -> GetActiveGroupsResponse:

    groups = [
        ActiveGroup(
            id=permission.item_id,
            name=permission.item_name,
        )
        for permission in permissions
    ]

    return GetActiveGroupsResponse(groups=groups)
