import logging

from access_control_service.models.models import (
    Conflict as ConflictModel,
)
from access_control_service.repositories.protocols import ConflictRepositoryProtocol

logger = logging.getLogger(__name__)


class ConflictService:

    def __init__(self, conflict_repository: ConflictRepositoryProtocol):
        self._conflict_repository = conflict_repository

    async def get_all_conflicts(self) -> list[ConflictModel]:

        conflicts = await self._conflict_repository.find_all()

        conflicts_out = [
            ConflictModel(group_id1=c.group_id1, group_id2=c.group_id2)
            for c in conflicts
        ]

        logger.debug(f"Найдено конфликтов: {len(conflicts_out)}")
        return conflicts_out

