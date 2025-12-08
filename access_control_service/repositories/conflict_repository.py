from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from access_control_service.db.conflict import Conflict
from access_control_service.repositories.protocols import ConflictRepositoryProtocol


class ConflictRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_group_ids(
        self, group_id1: int, group_id2: int
    ) -> Conflict | None:
        stmt = select(Conflict).where(
            Conflict.group_id1 == group_id1, Conflict.group_id2 == group_id2
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, conflict: Conflict) -> Conflict:
        self.session.add(conflict)
        await self.session.flush()
        return conflict

    async def delete(self, conflict: Conflict) -> None:
        await self.session.delete(conflict)
        await self.session.flush()

    async def flush(self) -> None:
        await self.session.flush()

    async def find_all(self) -> list[Conflict]:
        stmt = select(Conflict)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

