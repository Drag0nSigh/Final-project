from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from access_control_service.db.access import Access
from access_control_service.db.group import Group


class AccessRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id_with_resources(self, access_id: int) -> Access | None:
        stmt = (
            select(Access)
            .where(Access.id == access_id)
            .options(selectinload(Access.resources))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_with_groups(self, access_id: int) -> Access | None:
        stmt = (
            select(Access)
            .where(Access.id == access_id)
            .options(
                selectinload(Access.groups).selectinload(Group.accesses)
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all_with_resources(self) -> list[Access]:
        stmt = select(Access).options(selectinload(Access.resources))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, access: Access) -> Access:
        self._session.add(access)
        await self._session.flush()
        await self._session.refresh(access)
        return access

    async def flush(self) -> None:
        await self._session.flush()

    async def delete(self, access: Access) -> None:
        await self._session.delete(access)
        await self._session.flush()

    async def find_ids_by_ids(self, access_ids: list[int]) -> set[int]:
        stmt = select(Access.id).where(Access.id.in_(access_ids))
        result = await self._session.execute(stmt)
        return set(result.scalars().all())

    async def find_by_ids(self, access_ids: list[int]) -> list[Access]:
        stmt = select(Access).where(Access.id.in_(access_ids))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, access_id: int) -> Access | None:
        stmt = select(Access).where(Access.id == access_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
