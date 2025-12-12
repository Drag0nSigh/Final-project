from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from access_control_service.db.resource import Resource


class ResourceRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_ids_by_ids(self, resource_ids: list[int]) -> set[int]:
        stmt = select(Resource.id).where(Resource.id.in_(resource_ids))
        result = await self._session.execute(stmt)
        return set(result.scalars().all())

    async def find_by_ids(self, resource_ids: list[int]) -> list[Resource]:
        stmt = select(Resource).where(Resource.id.in_(resource_ids))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_id(self, resource_id: int) -> Resource | None:
        stmt = select(Resource).where(Resource.id == resource_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_id_with_accesses(self, resource_id: int) -> Resource | None:
        stmt = (
            select(Resource)
            .where(Resource.id == resource_id)
            .options(selectinload(Resource.accesses))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(self) -> list[Resource]:
        stmt = select(Resource)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, resource: Resource) -> Resource:
        self._session.add(resource)
        await self._session.flush()
        await self._session.refresh(resource)
        return resource

    async def delete(self, resource: Resource) -> None:
        await self._session.delete(resource)
        await self._session.flush()

    async def flush(self) -> None:
        await self._session.flush()
