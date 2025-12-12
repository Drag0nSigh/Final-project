import logging

from access_control_service.repositories.protocols import (
    AccessRepositoryProtocol,
    ResourceRepositoryProtocol,
)

logger = logging.getLogger(__name__)


class AccessServiceAdmin:

    def __init__(
        self,
        access_repository: AccessRepositoryProtocol,
        resource_repository: ResourceRepositoryProtocol,
    ):
        self._access_repository = access_repository
        self._resource_repository = resource_repository

    async def add_resource_to_access(
        self, access_id: int, resource_id: int
    ) -> None:

        logger.debug(
            f"Добавление ресурса к доступу: access_id={access_id}, resource_id={resource_id}"
        )

        access = await self._access_repository.find_by_id_with_resources(access_id)
        if access is None:
            raise ValueError(f"Доступ с ID {access_id} не найден")

        resource = await self._resource_repository.find_by_id(resource_id)
        if resource is None:
            raise ValueError(f"Ресурс с ID {resource_id} не найден")

        if resource in access.resources:
            raise ValueError(
                f"Ресурс {resource_id} уже привязан к доступу {access_id}"
            )

        access.resources.append(resource)
        await self._access_repository.flush()


    async def remove_resource_from_access(
        self, access_id: int, resource_id: int
    ) -> None:
        
        logger.debug(
            f"Удаление ресурса из доступа: access_id={access_id}, resource_id={resource_id}"
        )

        access = await self._access_repository.find_by_id_with_resources(access_id)
        if access is None:
            raise ValueError(f"Доступ с ID {access_id} не найден")

        resource_to_remove = None
        for res in access.resources:
            if res.id == resource_id:
                resource_to_remove = res
                break

        if resource_to_remove is None:
            raise ValueError(
                f"Ресурс {resource_id} не привязан к доступу {access_id}"
            )

        access.resources.remove(resource_to_remove)
        await self._access_repository.flush()

        logger.debug(
            f"Ресурс удален из доступа: access_id={access_id}, resource_id={resource_id}"
        )

    async def delete_access(self, access_id: int) -> None:

        logger.debug(f"Удаление доступа: id={access_id}")

        access_with_groups = await self._access_repository.find_by_id_with_groups(access_id)
        if access_with_groups is None:
            raise ValueError(f"Доступ с ID {access_id} не найден")

        if access_with_groups.groups:
            group_ids = [group.id for group in access_with_groups.groups]

            raise ValueError(
                f"Доступ с ID {access_id} не может быть удален, так как связан с группами: {group_ids}"
            )

        access_name = access_with_groups.name
        await self._access_repository.delete(access_with_groups)

        logger.debug(f"Доступ удален: id={access_id}, name={access_name}")

