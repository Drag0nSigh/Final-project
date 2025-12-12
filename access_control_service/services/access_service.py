import logging

from fastapi import HTTPException, status

from access_control_service.db.access import Access
from access_control_service.models.models import (
    CreateAccessRequest,
    CreateAccessResponse,
    GetAccessGroupsResponse,
    Resource as ResourceModel,
    Group as GroupModel,
    Access as AccessModel,
)
from access_control_service.repositories.protocols import (
    AccessRepositoryProtocol,
    ResourceRepositoryProtocol,
)

logger = logging.getLogger(__name__)


class AccessService:

    def __init__(
        self,
        access_repository: AccessRepositoryProtocol,
        resource_repository: ResourceRepositoryProtocol,
    ):
        self._access_repository = access_repository
        self._resource_repository = resource_repository

    async def create_access(
        self, access_data: CreateAccessRequest
    ) -> CreateAccessResponse:

        logger.debug(
            f"Создание доступа: name={access_data.name}, resource_ids={access_data.resource_ids}"
        )

        if access_data.resource_ids:
            existing_ids = await self._resource_repository.find_ids_by_ids(
                access_data.resource_ids
            )

            missing_ids = set(access_data.resource_ids) - existing_ids
            if missing_ids:
                raise ValueError(
                    f"Ресурсы с ID {sorted(missing_ids)} не найдены"
                )

        access = Access(name=access_data.name)
        access = await self._access_repository.save(access)
        access_id = access.id

        if access_data.resource_ids:
            resources = await self._resource_repository.find_by_ids(
                access_data.resource_ids
            )
            
            access_with_resources = await self._access_repository.find_by_id_with_resources(
                access_id
            )
            if access_with_resources is None:
                raise ValueError(f"Доступ с ID {access_id} не найден после создания")
            
            access_with_resources.resources.extend(resources)
            await self._access_repository.flush()
            
            access = access_with_resources
        else:
            access = await self._access_repository.find_by_id_with_resources(access_id)
            if access is None:
                raise ValueError(f"Доступ с ID {access_id} не найден после создания")

        logger.debug(
            f"Доступ создан: id={access.id}, name={access.name}, resources_count={len(access.resources)}"
        )

        resources_out = [
            ResourceModel(
                id=res.id,
                name=res.name,
                type=res.type,
                description=res.description,
            )
            for res in access.resources
        ]

        return CreateAccessResponse(
            id=access.id,
            name=access.name,
            resources=resources_out,
        )

    async def get_access(self, access_id: int) -> Access:
        
        logger.debug(f"Получение доступа: id={access_id}")

        access = await self._access_repository.find_by_id_with_resources(access_id)

        if access is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Доступ с ID {access_id} не найден"
            )

        logger.debug(
            f"Доступ найден: id={access.id}, name={access.name}, resources_count={len(access.resources)}"
        )
        return access

    async def get_all_accesses(self) -> list[Access]:

        logger.debug("Получение всех доступов")

        accesses = await self._access_repository.find_all_with_resources()

        logger.debug(f"Найдено доступов: {len(accesses)}")
        return accesses

    async def get_groups_containing_access(
        self, access_id: int
    ) -> GetAccessGroupsResponse:

        logger.debug(f"Получение групп для доступа: access_id={access_id}")

        access_with_groups = await self._access_repository.find_by_id_with_groups(access_id)
        if access_with_groups is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Доступ с ID {access_id} не найден"
            )

        groups = [
            GroupModel(
                id=group.id,
                name=group.name,
                accesses=[
                    AccessModel(
                        id=acc.id,
                        name=acc.name,
                        resources=[],  # Не загружаем ресурсы для каждого доступа
                    )
                    for acc in group.accesses
                ],
            )
            for group in access_with_groups.groups
        ]

        logger.debug(
            f"Найдено групп для доступа {access_id}: {len(groups)}"
        )

        return GetAccessGroupsResponse(access_id=access_id, groups=groups)

