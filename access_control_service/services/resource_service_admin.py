import logging

from access_control_service.db.resource import Resource
from access_control_service.models.models import (
    CreateResourceRequest,
    CreateResourceResponse,
)
from access_control_service.repositories.protocols import ResourceRepositoryProtocol

logger = logging.getLogger(__name__)


class ResourceServiceAdmin:

    def __init__(self, resource_repository: ResourceRepositoryProtocol):
        self._resource_repository = resource_repository

    async def create_resource(
        self, resource_data: CreateResourceRequest
    ) -> CreateResourceResponse:

        logger.debug(
            f"Создание ресурса: name={resource_data.name}, type={resource_data.type}"
        )

        resource = Resource(
            name=resource_data.name,
            type=resource_data.type,
            description=resource_data.description,
        )
        resource = await self._resource_repository.save(resource)

        logger.debug(f"Ресурс создан: id={resource.id}, name={resource.name}")
        return CreateResourceResponse(
            id=resource.id,
            name=resource.name,
            type=resource.type,
            description=resource.description,
        )

    async def delete_resource(self, resource_id: int) -> None:

        logger.debug(f"Удаление ресурса: id={resource_id}")

        resource = await self._resource_repository.find_by_id_with_accesses(resource_id)

        if resource is None:
            raise ValueError(f"Ресурс с ID {resource_id} не найден")

        if resource.accesses:
            access_ids = [acc.id for acc in resource.accesses]

            raise ValueError(
                f"Ресурс с ID {resource_id} не может быть удален, так как связан с доступами: {access_ids}"
            )

        await self._resource_repository.delete(resource)

        logger.debug(f"Ресурс удален: id={resource_id}, name={resource.name}")

