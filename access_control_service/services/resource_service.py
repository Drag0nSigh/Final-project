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
    """Сервис для работы с ресурсами."""

    @staticmethod
    async def create_resource(session: AsyncSession, resource_data: CreateResourceRequest) -> CreateResourceResponse:
        """Создание ресурса в БД."""
        
        logger.debug(f"Создание ресурса: name={resource_data.name}, type={resource_data.type}")

        resource = Resource(
            name=resource_data.name,
            type=resource_data.type,
            description=resource_data.description,
        )
        session.add(resource)
        await session.flush()
        await session.refresh(resource)

        logger.debug(f"Ресурс создан: id={resource.id}, name={resource.name}")
        return CreateResourceResponse(
            id=resource.id,
            name=resource.name,
            type=resource.type,
            description=resource.description,
        )

    @staticmethod
    async def get_resource(session: AsyncSession, resource_id: int) -> Resource:
        """Получение ресурса по ID."""
        
        logger.debug(f"Получение ресурса: id={resource_id}")

        stmt = select(Resource).where(Resource.id == resource_id)
        result = await session.execute(stmt)
        resource = result.scalar_one_or_none()

        if resource is None:
            raise ValueError(f"Ресурс с ID {resource_id} не найден")

        logger.debug(f"Ресурс найден: id={resource.id}, name={resource.name}")
        return resource

    @staticmethod
    async def get_all_resources(session: AsyncSession) -> list[Resource]:
        """Получение всех ресурсов."""
        
        logger.debug("Получение всех ресурсов")

        stmt = select(Resource)
        result = await session.execute(stmt)
        resources = result.scalars().all()

        logger.debug(f"Найдено ресурсов: {len(resources)}")
        return list(resources)

    @staticmethod
    async def delete_resource(session: AsyncSession, resource_id: int) -> None:
        """Удаление ресурса."""

        logger.debug(f"Удаление ресурса: id={resource_id}")

        stmt = (
            select(Resource)
            .where(Resource.id == resource_id)
            .options(selectinload(Resource.accesses))
        )
        result = await session.execute(stmt)
        resource = result.scalar_one_or_none()

        if resource is None:
            raise ValueError(f"Ресурс с ID {resource_id} не найден")

        if resource.accesses:
            access_ids = [acc.id for acc in resource.accesses]

            raise ValueError(
                f"Ресурс с ID {resource_id} не может быть удален, так как связан с доступами: {access_ids}"
            )

        session.delete(resource)
        await session.flush()

        logger.debug(f"Ресурс удален: id={resource_id}, name={resource.name}")

