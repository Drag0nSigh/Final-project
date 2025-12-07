import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from access_control_service.db.resource import Resource
from access_control_service.models.models import (
    CreateResourceRequest,
    CreateResourceResponse,
)

logger = logging.getLogger(__name__)


class ResourceService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_resource(self, resource_data: CreateResourceRequest) -> CreateResourceResponse:
        
        logger.debug(f"Создание ресурса: name={resource_data.name}, type={resource_data.type}")

        resource = Resource(
            name=resource_data.name,
            type=resource_data.type,
            description=resource_data.description,
        )
        self.session.add(resource)
        await self.session.flush()
        await self.session.refresh(resource)

        logger.debug(f"Ресурс создан: id={resource.id}, name={resource.name}")
        return CreateResourceResponse(
            id=resource.id,
            name=resource.name,
            type=resource.type,
            description=resource.description,
        )

    async def get_resource(self, resource_id: int) -> Resource:
        
        logger.debug(f"Получение ресурса: id={resource_id}")

        stmt = select(Resource).where(Resource.id == resource_id)
        result = await self.session.execute(stmt)
        resource = result.scalar_one_or_none()

        if resource is None:
            raise ValueError(f"Ресурс с ID {resource_id} не найден")

        logger.debug(f"Ресурс найден: id={resource.id}, name={resource.name}")
        return resource

    async def get_all_resources(self) -> list[Resource]:
        
        logger.debug("Получение всех ресурсов")

        stmt = select(Resource)
        result = await self.session.execute(stmt)
        resources = result.scalars().all()

        logger.debug(f"Найдено ресурсов: {len(resources)}")
        return list(resources)

    async def delete_resource(self, resource_id: int) -> None:

        logger.debug(f"Удаление ресурса: id={resource_id}")

        stmt = (
            select(Resource)
            .where(Resource.id == resource_id)
            .options(selectinload(Resource.accesses))
        )
        result = await self.session.execute(stmt)
        resource = result.scalar_one_or_none()

        if resource is None:
            raise ValueError(f"Ресурс с ID {resource_id} не найден")

        if resource.accesses:
            access_ids = [acc.id for acc in resource.accesses]

            raise ValueError(
                f"Ресурс с ID {resource_id} не может быть удален, так как связан с доступами: {access_ids}"
            )

        self.session.delete(resource)
        await self.session.flush()

        logger.debug(f"Ресурс удален: id={resource_id}, name={resource.name}")

