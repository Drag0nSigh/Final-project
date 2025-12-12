from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from access_control_service.db.group import Group
from access_control_service.db.access import Access


class GroupRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_ids_by_ids(self, group_ids: list[int]) -> set[int]:
        stmt = select(Group.id).where(Group.id.in_(group_ids))
        result = await self._session.execute(stmt)
        return set(result.scalars().all())

    async def find_by_id_with_accesses_and_resources(self, group_id: int) -> Group | None:
        stmt = (
            select(Group)
            .where(Group.id == group_id)
            .options(
                selectinload(Group.accesses).selectinload(Access.resources)
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all_with_accesses_and_resources(self) -> list[Group]:
        stmt = (
            select(Group)
            .options(
                selectinload(Group.accesses).selectinload(Access.resources)
            )
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id_with_accesses(self, group_id: int) -> Group | None:
        stmt = (
            select(Group)
            .where(Group.id == group_id)
            .options(selectinload(Group.accesses))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_with_conflicts(self, group_id: int) -> Group | None:
        stmt = (
            select(Group)
            .where(Group.id == group_id)
            .options(
                selectinload(Group.conflicts_as_group1),
                selectinload(Group.conflicts_as_group2)
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_name(self, name: str) -> Group | None:
        stmt = select(Group).where(Group.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, group: Group) -> Group:
        self._session.add(group)
        await self._session.flush()
        await self._session.refresh(group)
        return group

    async def flush(self) -> None:
        await self._session.flush()

    async def delete(self, group: Group) -> None:
        await self._session.delete(group)
        await self._session.flush()
