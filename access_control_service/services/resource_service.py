import logging

from access_control_service.db.resource import Resource
from access_control_service.repositories.protocols import ResourceRepositoryProtocol

logger = logging.getLogger(__name__)


class ResourceService:

    def __init__(self, resource_repository: ResourceRepositoryProtocol):
        self._resource_repository = resource_repository

    async def get_resource(self, resource_id: int) -> Resource:

        logger.debug(f"Получение ресурса: id={resource_id}")

        resource = await self._resource_repository.find_by_id(resource_id)

        if resource is None:
            raise ValueError(f"Ресурс с ID {resource_id} не найден")

        logger.debug(f"Ресурс найден: id={resource.id}, name={resource.name}")
        return resource

    async def get_all_resources(self) -> list[Resource]:

        logger.debug("Получение всех ресурсов")

        resources = await self._resource_repository.find_all()

        logger.debug(f"Найдено ресурсов: {len(resources)}")
        return resources

