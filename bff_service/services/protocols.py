from typing import Protocol, Any

from bff_service.models.models import (
    Resource,
    Access,
    Group,
    GetConflictsResponse,
    RequestAccessResponse,
    RevokePermissionResponse,
    GetUserPermissionsResponse,
)


class HTTPClientProtocol(Protocol):

    async def get(self, url: str, **kwargs: Any) -> Any:
        ...

    async def post(self, url: str, **kwargs: Any) -> Any:
        ...

    async def request(self, method: str, url: str, **kwargs: Any) -> Any:
        ...

    async def aclose(self) -> None:
        ...


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


class ResourceClientProtocol(Protocol):

    async def get_all(self) -> list[Resource]:
        ...

    async def get_by_id(self, resource_id: int) -> Resource:
        ...


class AccessClientProtocol(Protocol):

    async def get_all(self) -> list[Access]:
        ...

    async def get_by_id(self, access_id: int) -> Access:
        ...


class GroupClientProtocol(Protocol):

    async def get_all(self) -> list[Group]:
        ...

    async def get_by_id(self, group_id: int) -> Group:
        ...


class ConflictClientProtocol(Protocol):

    async def get_all(self) -> GetConflictsResponse:
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

