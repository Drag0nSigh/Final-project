from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from user_service.db.userpermission import UserPermission
from user_service.repositories.protocols import UserPermissionRepositoryProtocol


class UserPermissionRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, permission_id: int) -> UserPermission | None:
        stmt = select(UserPermission).where(UserPermission.id == permission_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_user_id(self, user_id: int) -> list[UserPermission]:
        stmt = select(UserPermission).where(UserPermission.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_user_id_and_permission_type(
        self,
        user_id: int,
        permission_type: str,
        item_id: int
    ) -> UserPermission | None:
        stmt = select(UserPermission).where(
            UserPermission.user_id == user_id,
            UserPermission.permission_type == permission_type,
            UserPermission.item_id == item_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_user_id_and_type_and_status(
        self,
        user_id: int,
        permission_type: str,
        statuses: list[str]
    ) -> UserPermission | None:
        stmt = select(UserPermission).where(
            UserPermission.user_id == user_id,
            UserPermission.permission_type == permission_type,
            UserPermission.status.in_(statuses),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_user_id_and_type_and_item_and_status(
        self,
        user_id: int,
        permission_type: str,
        item_id: int,
        statuses: list[str]
    ) -> UserPermission | None:
        stmt = select(UserPermission).where(
            UserPermission.user_id == user_id,
            UserPermission.permission_type == permission_type,
            UserPermission.item_id == item_id,
            UserPermission.status.in_(statuses),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_request_id(self, request_id: str) -> UserPermission | None:
        stmt = select(UserPermission).where(UserPermission.request_id == request_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_active_groups_by_user_id(self, user_id: int) -> list[UserPermission]:
        stmt = select(UserPermission).where(
            UserPermission.user_id == user_id,
            UserPermission.permission_type == "group",
            UserPermission.status == "active",
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, permission: UserPermission) -> UserPermission:
        self.session.add(permission)
        await self.session.flush()
        await self.session.refresh(permission)
        return permission

    async def flush(self) -> None:
        await self.session.flush()

    async def delete(self, permission: UserPermission) -> None:
        self.session.delete(permission)
        await self.session.flush()

