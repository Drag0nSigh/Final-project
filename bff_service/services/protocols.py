from typing import Protocol, Any


class UserServiceClientProtocol(Protocol):

    async def request_access(
        self, user_id: int, permission_type: str, item_id: int
    ) -> dict[str, Any]:
        ...

    async def revoke_permission(
        self, user_id: int, permission_type: str, item_id: int
    ) -> dict[str, Any]:
        ...

    async def get_user_permissions(self, user_id: int) -> dict[str, Any]:
        ...

    async def close(self) -> None:
        ...


class AccessControlClientProtocol(Protocol):

    async def get_all_resources(self) -> list[dict[str, Any]]:
        ...

    async def get_resource(self, resource_id: int) -> dict[str, Any]:
        ...

    async def get_all_accesses(self) -> list[dict[str, Any]]:
        ...

    async def get_access(self, access_id: int) -> dict[str, Any]:
        ...

    async def get_all_groups(self) -> list[dict[str, Any]]:
        ...

    async def get_group(self, group_id: int) -> dict[str, Any]:
        ...

    async def get_conflicts(self) -> dict[str, Any]:
        ...

    async def close(self) -> None:
        ...

