from typing import Protocol

from user_service.db.user import User
from user_service.db.userpermission import UserPermission


class UserRepositoryProtocol(Protocol):

    async def find_by_id(self, user_id: int) -> User | None:
        ...

    async def find_by_username(self, username: str) -> User | None:
        ...

    async def find_all(self) -> list[User]:
        ...

    async def save(self, user: User) -> User:
        ...

    async def flush(self) -> None:
        ...

    async def delete(self, user: User) -> None:
        ...


class UserPermissionRepositoryProtocol(Protocol):

    async def find_by_id(self, permission_id: int) -> UserPermission | None:
        ...

    async def find_by_user_id(self, user_id: int) -> list[UserPermission]:
        ...

    async def find_by_user_id_and_permission_type(
        self,
        user_id: int,
        permission_type: str,
        item_id: int
    ) -> UserPermission | None:
        ...

    async def find_by_user_id_and_type_and_status(
        self,
        user_id: int,
        permission_type: str,
        statuses: list[str]
    ) -> UserPermission | None:
        ...

    async def find_by_user_id_and_type_and_item_and_status(
        self,
        user_id: int,
        permission_type: str,
        item_id: int,
        statuses: list[str]
    ) -> UserPermission | None:
        ...

    async def find_by_request_id(self, request_id: str) -> UserPermission | None:
        ...

    async def find_active_groups_by_user_id(self, user_id: int) -> list[UserPermission]:
        ...

    async def save(self, permission: UserPermission) -> UserPermission:
        ...

    async def flush(self) -> None:
        ...

    async def delete(self, permission: UserPermission) -> None:
        ...
