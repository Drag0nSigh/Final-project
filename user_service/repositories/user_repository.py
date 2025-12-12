from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from user_service.db.user import User


class UserRepository:

    def __init__(self, session: AsyncSession):
        self._session = session

    async def find_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(self) -> list[User]:
        stmt = select(User)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def save(self, user: User) -> User:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def flush(self) -> None:
        await self._session.flush()

    async def delete(self, user: User) -> None:
        await self._session.delete(user)
        await self._session.flush()
