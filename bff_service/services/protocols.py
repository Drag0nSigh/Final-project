from typing import Protocol

from bff_service.models.models import (
    Resource,
    Access,
    Group,
    GetConflictsResponse,
    RequestAccessResponse,
    RevokePermissionResponse,
    GetUserPermissionsResponse,
)


class UserServiceClientProtocol(Protocol):

    async def request_access(
        self, user_id: int, permission_type: str, item_id: int
    ) -> RequestAccessResponse:
        ...

    async def revoke_permission(
        self, user_id: int, permission_type: str, item_id: int
    ) -> RevokePermissionResponse:
        ...

    async def get_user_permissions(self, user_id: int) -> GetUserPermissionsResponse:
        ...

    async def close(self) -> None:
        ...


class AccessControlClientProtocol(Protocol):

    async def get_all_resources(self) -> list[Resource]:
        ...

    async def get_resource(self, resource_id: int) -> Resource:
        ...

    async def get_all_accesses(self) -> list[Access]:
        ...

    async def get_access(self, access_id: int) -> Access:
        ...

    async def get_all_groups(self) -> list[Group]:
        ...

    async def get_group(self, group_id: int) -> Group:
        ...

    async def get_conflicts(self) -> GetConflictsResponse:
        ...

    async def close(self) -> None:
        ...

