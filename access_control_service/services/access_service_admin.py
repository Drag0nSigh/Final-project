import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from access_control_service.db.access import Access
from access_control_service.db.resource import Resource

logger = logging.getLogger(__name__)


class AccessServiceAdmin:

    @staticmethod
    async def add_resource_to_access(
        session: AsyncSession, access_id: int, resource_id: int
    ) -> None:

        logger.debug(
            f"Добавление ресурса к доступу: access_id={access_id}, resource_id={resource_id}"
        )

        stmt = (
            select(Access)
            .where(Access.id == access_id)
            .options(selectinload(Access.resources))
        )
        result = await session.execute(stmt)
        access = result.scalar_one_or_none()
        if access is None:
            raise ValueError(f"Доступ с ID {access_id} не найден")

        stmt = select(Resource).where(Resource.id == resource_id)
        result = await session.execute(stmt)
        resource = result.scalar_one_or_none()
        if resource is None:
            raise ValueError(f"Ресурс с ID {resource_id} не найден")

        if resource in access.resources:
            raise ValueError(
                f"Ресурс {resource_id} уже привязан к доступу {access_id}"
            )

        access.resources.append(resource)
        await session.flush()


    @staticmethod
    async def remove_resource_from_access(
        session: AsyncSession, access_id: int, resource_id: int
    ) -> None:
        
        logger.debug(
            f"Удаление ресурса из доступа: access_id={access_id}, resource_id={resource_id}"
        )

        stmt = (
            select(Access)
            .where(Access.id == access_id)
            .options(selectinload(Access.resources))
        )
        result = await session.execute(stmt)
        access = result.scalar_one_or_none()
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
        await session.flush()

        logger.debug(
            f"Ресурс удален из доступа: access_id={access_id}, resource_id={resource_id}"
        )

    @staticmethod
    async def delete_access(session: AsyncSession, access_id: int) -> None:

        logger.debug(f"Удаление доступа: id={access_id}")

        stmt = select(Access).where(Access.id == access_id)
        result = await session.execute(stmt)
        access = result.scalar_one_or_none()
        if access is None:
            raise ValueError(f"Доступ с ID {access_id} не найден")

        stmt = (
            select(Access)
            .where(Access.id == access_id)
            .options(selectinload(Access.groups))
        )
        result = await session.execute(stmt)
        access_with_groups = result.scalar_one()

        if access_with_groups.groups:
            group_ids = [group.id for group in access_with_groups.groups]

            raise ValueError(
                f"Доступ с ID {access_id} не может быть удален, так как связан с группами: {group_ids}"
            )

        access_name = access_with_groups.name
        session.delete(access_with_groups)
        await session.flush()

        logger.debug(f"Доступ удален: id={access_id}, name={access_name}")

