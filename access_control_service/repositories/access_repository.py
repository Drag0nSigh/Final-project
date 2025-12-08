from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from access_control_service.db.access import Access
from access_control_service.db.group import Group
from access_control_service.repositories.protocols import AccessRepositoryProtocol


class AccessRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id_with_resources(self, access_id: int) -> Access | None:
        stmt = (
            select(Access)
            .where(Access.id == access_id)
            .options(selectinload(Access.resources))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_with_groups(self, access_id: int) -> Access | None:
        stmt = (
            select(Access)
            .where(Access.id == access_id)
            .options(
                selectinload(Access.groups).selectinload(Group.accesses)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all_with_resources(self) -> list[Access]:
        stmt = select(Access).options(selectinload(Access.resources))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, access: Access) -> Access:
        self.session.add(access)
        await self.session.flush()
        await self.session.refresh(access)
        return access

    async def flush(self) -> None:
        await self.session.flush()

    async def delete(self, access: Access) -> None:
        self.session.delete(access)
        await self.session.flush()

    async def find_ids_by_ids(self, access_ids: list[int]) -> set[int]:
        stmt = select(Access.id).where(Access.id.in_(access_ids))
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    async def find_by_ids(self, access_ids: list[int]) -> list[Access]:
        stmt = select(Access).where(Access.id.in_(access_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, access_id: int) -> Access | None:
        stmt = select(Access).where(Access.id == access_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

