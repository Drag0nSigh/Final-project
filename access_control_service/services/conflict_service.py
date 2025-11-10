import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from access_control_service.db.conflict import Conflict
from access_control_service.models.models import (
    Conflict as ConflictModel,
)

logger = logging.getLogger(__name__)


class ConflictService:
    """Сервис для работы с конфликтами между группами"""

    @staticmethod
    async def get_all_conflicts(session: AsyncSession) -> list[ConflictModel]:
        """Получение всех конфликтов."""

        stmt = select(Conflict)
        result = await session.execute(stmt)
        conflicts = result.scalars().all()

        conflicts_out = [
            ConflictModel(group_id1=c.group_id1, group_id2=c.group_id2)
            for c in conflicts
        ]

        logger.debug(f"Найдено конфликтов: {len(conflicts_out)}")
        return conflicts_out

