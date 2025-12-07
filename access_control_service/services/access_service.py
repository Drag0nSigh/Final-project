import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from access_control_service.db.access import Access
from access_control_service.db.resource import Resource
from access_control_service.db.group import Group
from access_control_service.models.models import (
    CreateAccessRequest,
    CreateAccessResponse,
    GetAccessGroupsResponse,
    Resource as ResourceModel,
    Group as GroupModel,
    Access as AccessModel,
)

logger = logging.getLogger(__name__)


class AccessService:

    @staticmethod
    async def create_access(
        session: AsyncSession, access_data: CreateAccessRequest
    ) -> CreateAccessResponse:

        logger.debug(
            f"Создание доступа: name={access_data.name}, resource_ids={access_data.resource_ids}"
        )

        if access_data.resource_ids:
            stmt = select(Resource.id).where(Resource.id.in_(access_data.resource_ids))
            result = await session.execute(stmt)
            existing_ids = set(result.scalars().all())

            missing_ids = set(access_data.resource_ids) - existing_ids
            if missing_ids:
                raise ValueError(
                    f"Ресурсы с ID {sorted(missing_ids)} не найдены"
                )

        access = Access(name=access_data.name)
        session.add(access)
        await session.flush()
        await session.refresh(access)

        if access_data.resource_ids:
            stmt = select(Resource).where(Resource.id.in_(access_data.resource_ids))
            result = await session.execute(stmt)
            resources = result.scalars().all()
            
            stmt = (
                select(Access)
                .where(Access.id == access.id)
                .options(selectinload(Access.resources))
            )
            result = await session.execute(stmt)
            access_with_resources = result.scalar_one()
            access_with_resources.resources.extend(resources)
            await session.flush()
            
            access = access_with_resources
        else:
            stmt = (
                select(Access)
                .where(Access.id == access.id)
                .options(selectinload(Access.resources))
            )
            result = await session.execute(stmt)
            access = result.scalar_one()

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

    @staticmethod
    async def get_access(session: AsyncSession, access_id: int) -> Access:
        
        logger.debug(f"Получение доступа: id={access_id}")

        stmt = (
            select(Access)
            .where(Access.id == access_id)
            .options(selectinload(Access.resources))
        )
        result = await session.execute(stmt)
        access = result.scalar_one_or_none()

        if access is None:
            raise ValueError(f"Доступ с ID {access_id} не найден")

        logger.debug(
            f"Доступ найден: id={access.id}, name={access.name}, resources_count={len(access.resources)}"
        )
        return access

    @staticmethod
    async def get_all_accesses(session: AsyncSession) -> list[Access]:

        logger.debug("Получение всех доступов")

        stmt = select(Access).options(selectinload(Access.resources))
        result = await session.execute(stmt)
        accesses = result.scalars().all()

        logger.debug(f"Найдено доступов: {len(accesses)}")
        return list(accesses)

    @staticmethod
    async def get_groups_containing_access(
        session: AsyncSession, access_id: int
    ) -> GetAccessGroupsResponse:

        logger.debug(f"Получение групп для доступа: access_id={access_id}")

        stmt = select(Access).where(Access.id == access_id)
        result = await session.execute(stmt)
        access = result.scalar_one_or_none()
        if access is None:
            raise ValueError(f"Доступ с ID {access_id} не найден")

        stmt = (
            select(Access)
            .where(Access.id == access_id)
            .options(
                selectinload(Access.groups).selectinload(Group.accesses)
            )
        )
        result = await session.execute(stmt)
        access_with_groups = result.scalar_one()

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

