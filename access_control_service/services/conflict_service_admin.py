import logging

from access_control_service.db.conflict import Conflict
from access_control_service.models.models import (
    CreateConflictRequest,
    CreateConflictResponse,
    GetConflictsResponse,
)
from access_control_service.repositories.protocols import (
    GroupRepositoryProtocol,
    ConflictRepositoryProtocol,
)

logger = logging.getLogger(__name__)


class ConflictServiceAdmin:

    def __init__(
        self,
        group_repository: GroupRepositoryProtocol,
        conflict_repository: ConflictRepositoryProtocol,
    ):
        self.group_repository = group_repository
        self.conflict_repository = conflict_repository

    async def create_conflict(
        self, conflict_data: CreateConflictRequest
    ) -> list[CreateConflictResponse]:

        group_id1 = conflict_data.group_id1
        group_id2 = conflict_data.group_id2

        if group_id1 == group_id2:
            raise ValueError("Группа не может конфликтовать сама с собой")

        logger.debug(
            f"Создание конфликта: group_id1={group_id1}, group_id2={group_id2}"
        )

        existing_ids = await self.group_repository.find_ids_by_ids(
            [group_id1, group_id2]
        )

        missing_ids = {group_id1, group_id2} - existing_ids
        if missing_ids:
            raise ValueError(f"Группы с ID {sorted(missing_ids)} не найдены")

        created_conflicts = []

        for g1, g2 in [(group_id1, group_id2), (group_id2, group_id1)]:
            existing_conflict = await self.conflict_repository.find_by_group_ids(g1, g2)

            if existing_conflict is None:
                conflict = Conflict(group_id1=g1, group_id2=g2)
                await self.conflict_repository.save(conflict)
                created_conflicts.append(
                    CreateConflictResponse(group_id1=g1, group_id2=g2)
                )
                logger.info(f"Создан конфликт: group_id1={g1}, group_id2={g2}")
            else:
                logger.debug(
                    f"Конфликт уже существует: group_id1={g1}, group_id2={g2}"
                )
                created_conflicts.append(
                    CreateConflictResponse(group_id1=g1, group_id2=g2)
                )

        logger.info(
            f"Конфликт создан: group_id1={group_id1}, group_id2={group_id2}, "
            f"создано пар: {len(created_conflicts)}"
        )

        return created_conflicts

    async def delete_conflict(
        self, group_id1: int, group_id2: int
    ) -> None:
        """Удаление конфликта между группами.

        Удаляет обе симметричные пары: (group_id1, group_id2) и (group_id2, group_id1).
        """

        logger.debug(
            f"Удаление конфликта: group_id1={group_id1}, group_id2={group_id2}"
        )

        deleted_count = 0

        for g1, g2 in [(group_id1, group_id2), (group_id2, group_id1)]:
            conflict = await self.conflict_repository.find_by_group_ids(g1, g2)
            logger.debug(f"conflict: {conflict.group_id1}, {conflict.group_id2}" if conflict else "conflict: None")

            if conflict is not None:
                await self.conflict_repository.delete(conflict)
                deleted_count += 1
                logger.debug(f"Удален конфликт: group_id1={g1}, group_id2={g2}")
            else:
                logger.debug(
                    f"Конфликт не найден: group_id1={g1}, group_id2={g2}"
                )
        found_conflict = await self.conflict_repository.find_by_group_ids(group_id1, group_id2) # DEBUG
        logger.debug(f"{found_conflict}" if found_conflict else "found_conflict: None") # DEBUG
        if deleted_count == 0:

            raise ValueError(
                f"Конфликт между группами {group_id1} и {group_id2} не найден"
            )
        logger.debug(
            f"Конфликт удален: group_id1={group_id1}, group_id2={group_id2}, "
            f"удалено пар: {deleted_count}"
        )

