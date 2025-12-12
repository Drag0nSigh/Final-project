import logging

from access_control_service.db.group import Group
from access_control_service.models.models import (
    CreateGroupRequest,
    CreateGroupResponse,
    GetGroupAccessesResponse,
    Access as AccessModel,
    Resource as ResourceModel,
)
from access_control_service.repositories.protocols import (
    GroupRepositoryProtocol,
    AccessRepositoryProtocol,
    ConflictRepositoryProtocol,
)

logger = logging.getLogger(__name__)


class GroupService:

    def __init__(
        self,
        group_repository: GroupRepositoryProtocol,
        access_repository: AccessRepositoryProtocol,
        conflict_repository: ConflictRepositoryProtocol,
    ):
        self._group_repository = group_repository
        self._access_repository = access_repository
        self._conflict_repository = conflict_repository

    async def create_group(
        self, group_data: CreateGroupRequest
    ) -> CreateGroupResponse:

        logger.debug(
            f"Создание группы: name={group_data.name}, access_ids={group_data.access_ids}"
        )

        existing_group = await self._group_repository.find_by_name(group_data.name)
        if existing_group is not None:
            raise ValueError(f"Группа с именем '{group_data.name}' уже существует")

        if group_data.access_ids:
            existing_ids = await self._access_repository.find_ids_by_ids(
                group_data.access_ids
            )

            missing_ids = set(group_data.access_ids) - existing_ids
            if missing_ids:
                raise ValueError(
                    f"Доступы с ID {sorted(missing_ids)} не найдены"
                )

        group = Group(name=group_data.name)
        group = await self._group_repository.save(group)
        group_id = group.id

        if group_data.access_ids:
            accesses = await self._access_repository.find_by_ids(
                group_data.access_ids
            )
            
            group_with_accesses = await self._group_repository.find_by_id_with_accesses(group_id)
            if group_with_accesses is None:
                raise ValueError(f"Группа с ID {group_id} не найдена после создания")
            
            group_with_accesses.accesses.extend(accesses)
            await self._group_repository.flush()
            
            group = group_with_accesses
        else:
            group = await self._group_repository.find_by_id_with_accesses(group_id)
            if group is None:
                raise ValueError(f"Группа с ID {group_id} не найдена после создания")

        logger.debug(
            f"Группа создана: id={group.id}, name={group.name}, accesses_count={len(group.accesses)}"
        )

        accesses_out = [
            AccessModel(
                id=acc.id,
                name=acc.name,
                resources=[],  # Не загружаем ресурсы для каждого доступа
            )
            for acc in group.accesses
        ]

        return CreateGroupResponse(
            id=group.id,
            name=group.name,
            accesses=accesses_out,
        )

    async def get_group(self, group_id: int) -> Group:

        logger.debug(f"Получение группы: id={group_id}")

        group = await self._group_repository.find_by_id_with_accesses_and_resources(group_id)

        if group is None:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        logger.debug(
            f"Группа найдена: id={group.id}, name={group.name}, accesses_count={len(group.accesses)}"
        )
        return group

    async def get_all_groups(self) -> list[Group]:

        logger.debug("Получение всех групп")

        groups = await self._group_repository.find_all_with_accesses_and_resources()

        logger.debug(f"Найдено групп: {len(groups)}")
        return groups

    async def get_group_accesses(
        self, group_id: int
    ) -> GetGroupAccessesResponse:

        logger.debug(f"Получение доступов для группы: group_id={group_id}")

        group_with_accesses = await self.group_repository.find_by_id_with_accesses_and_resources(group_id)
        
        if group_with_accesses is None:
            logger.warning(f"Группа не найдена: id={group_id}")
            raise ValueError(f"Группа с ID {group_id} не найдена")

        accesses = [
            AccessModel(
                id=access.id,
                name=access.name,
                resources=[
                    ResourceModel(
                        id=res.id,
                        name=res.name,
                        type=res.type,
                        description=res.description,
                    )
                    for res in access.resources
                ],
            )
            for access in group_with_accesses.accesses
        ]

        logger.debug(
            f"Найдено доступов для группы {group_id}: {len(accesses)}"
        )

        return GetGroupAccessesResponse(group_id=group_id, accesses=accesses)

    async def add_access_to_group(
        self, group_id: int, access_id: int
    ) -> None:

        group = await self.group_repository.find_by_id_with_accesses(group_id)
        if group is None:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        access = await self._access_repository.find_by_id(access_id)
        if access is None:
            raise ValueError(f"Доступ с ID {access_id} не найден")

        if access in group.accesses:
            raise ValueError(
                f"Доступ {access_id} уже привязан к группе {group_id}"
            )

        group.accesses.append(access)
        await self.group_repository.flush()

    async def remove_access_from_group(
        self, group_id: int, access_id: int
    ) -> None:

        group = await self.group_repository.find_by_id_with_accesses(group_id)
        if group is None:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        access_to_remove = None
        for acc in group.accesses:
            if acc.id == access_id:
                access_to_remove = acc
                break

        if access_to_remove is None:
            raise ValueError(
                f"Доступ {access_id} не привязан к группе {group_id}"
            )

        group.accesses.remove(access_to_remove)
        await self.group_repository.flush()

    async def delete_group(self, group_id: int) -> None:

        group = await self._group_repository.find_by_id_with_conflicts(group_id)
        if group is None:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        conflicts = list(group.conflicts_as_group1) + list(group.conflicts_as_group2)
        if conflicts:
            raise ValueError(
                f"Группа с ID {group_id} не может быть удалена, так как имеет конфликты"
            )

        await self._group_repository.delete(group)


