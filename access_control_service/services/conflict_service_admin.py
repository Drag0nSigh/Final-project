import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from access_control_service.db.conflict import Conflict
from access_control_service.db.group import Group
from access_control_service.models.models import (
    CreateConflictIn,
    CreateConflictOut,
)

logger = logging.getLogger(__name__)


class ConflictServiceAdmin:
    """Служебные методы для управления конфликтами."""

    @staticmethod
    async def create_conflict(
        session: AsyncSession, conflict_data: CreateConflictIn
    ) -> list[CreateConflictOut]:
        """Создание конфликта между группами с автоматической симметрией."""

        group_id1 = conflict_data.group_id1
        group_id2 = conflict_data.group_id2

        if group_id1 == group_id2:
            raise ValueError("Группа не может конфликтовать сама с собой")

        logger.debug(
            f"Создание конфликта: group_id1={group_id1}, group_id2={group_id2}"
        )

        stmt = select(Group).where(Group.id.in_([group_id1, group_id2]))
        result = await session.execute(stmt)
        existing_groups = result.scalars().all()
        existing_group_ids = {g.id for g in existing_groups}

        missing_ids = {group_id1, group_id2} - existing_group_ids
        if missing_ids:
            raise ValueError(f"Группы с ID {sorted(missing_ids)} не найдены")

        created_conflicts = []

        for g1, g2 in [(group_id1, group_id2), (group_id2, group_id1)]:
            stmt = select(Conflict).where(
                Conflict.group_id1 == g1, Conflict.group_id2 == g2
            )
            result = await session.execute(stmt)
            existing_conflict = result.scalar_one_or_none()

            if existing_conflict is None:
                conflict = Conflict(group_id1=g1, group_id2=g2)
                session.add(conflict)
                await session.flush()
                created_conflicts.append(
                    CreateConflictOut(group_id1=g1, group_id2=g2)
                )
                logger.info(f"Создан конфликт: group_id1={g1}, group_id2={g2}")
            else:
                logger.debug(
                    f"Конфликт уже существует: group_id1={g1}, group_id2={g2}"
                )
                created_conflicts.append(
                    CreateConflictOut(group_id1=g1, group_id2=g2)
                )

        logger.info(
            f"Конфликт создан: group_id1={group_id1}, group_id2={group_id2}, "
            f"создано пар: {len(created_conflicts)}"
        )

        return created_conflicts

    @staticmethod
    async def delete_conflict(
        session: AsyncSession, group_id1: int, group_id2: int
    ) -> None:
        """Удаление конфликта между группами.

        Удаляет обе симметричные пары: (group_id1, group_id2) и (group_id2, group_id1).
        """

        logger.debug(
            f"Удаление конфликта: group_id1={group_id1}, group_id2={group_id2}"
        )

        deleted_count = 0

        for g1, g2 in [(group_id1, group_id2), (group_id2, group_id1)]:
            stmt = select(Conflict).where(
                Conflict.group_id1 == g1, Conflict.group_id2 == g2
            )
            result = await session.execute(stmt)
            conflict = result.scalar_one_or_none()

            if conflict is not None:
                await session.delete(conflict)
                await session.flush()
                deleted_count += 1
                logger.debug(f"Удален конфликт: group_id1={g1}, group_id2={g2}")
            else:
                logger.debug(
                    f"Конфликт не найден: group_id1={g1}, group_id2={g2}"
                )

        if deleted_count == 0:

            raise ValueError(
                f"Конфликт между группами {group_id1} и {group_id2} не найден"
            )

        logger.debug(
            f"Конфликт удален: group_id1={group_id1}, group_id2={group_id2}, "
            f"удалено пар: {deleted_count}"
        )

