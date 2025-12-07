import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from access_control_service.db.group import Group
from access_control_service.db.access import Access
from access_control_service.models.models import (
    CreateGroupRequest,
    CreateGroupResponse,
    GetGroupAccessesResponse,
    Access as AccessModel,
    Resource as ResourceModel,
)

logger = logging.getLogger(__name__)


class GroupService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_group(
        self, group_data: CreateGroupRequest
    ) -> CreateGroupResponse:

        logger.debug(
            f"Создание группы: name={group_data.name}, access_ids={group_data.access_ids}"
        )

        if group_data.access_ids:
            stmt = select(Access.id).where(Access.id.in_(group_data.access_ids))
            result = await self.session.execute(stmt)
            existing_ids = set(result.scalars().all())

            missing_ids = set(group_data.access_ids) - existing_ids
            if missing_ids:
                raise ValueError(
                    f"Доступы с ID {sorted(missing_ids)} не найдены"
                )

        group = Group(name=group_data.name)
        self.session.add(group)
        await self.session.flush()
        await self.session.refresh(group)

        if group_data.access_ids:
            stmt = select(Access).where(Access.id.in_(group_data.access_ids))
            result = await self.session.execute(stmt)
            accesses = result.scalars().all()
            
            stmt = (
                select(Group)
                .where(Group.id == group.id)
                .options(selectinload(Group.accesses))
            )
            result = await self.session.execute(stmt)
            group_with_accesses = result.scalar_one()
            group_with_accesses.accesses.extend(accesses)
            await self.session.flush()
            
            group = group_with_accesses

        await self.session.refresh(group, ["accesses"])

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

        stmt = (
            select(Group)
            .where(Group.id == group_id)
            .options(
                selectinload(Group.accesses).selectinload(Access.resources)
            )
        )
        result = await self.session.execute(stmt)
        group = result.scalar_one_or_none()

        if group is None:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        logger.debug(
            f"Группа найдена: id={group.id}, name={group.name}, accesses_count={len(group.accesses)}"
        )
        return group

    async def get_all_groups(self) -> list[Group]:

        logger.debug("Получение всех групп")

        stmt = (
            select(Group)
            .options(
                selectinload(Group.accesses).selectinload(Access.resources)
            )
        )
        result = await self.session.execute(stmt)
        groups = result.scalars().all()

        logger.debug(f"Найдено групп: {len(groups)}")
        return list(groups)

    async def get_group_accesses(
        self, group_id: int
    ) -> GetGroupAccessesResponse:

        logger.debug(f"Получение доступов для группы: group_id={group_id}")

        stmt = (
            select(Group)
            .where(Group.id == group_id)
            .options(
                selectinload(Group.accesses).selectinload(Access.resources)
            )
        )
        result = await self.session.execute(stmt)
        group_with_accesses = result.scalar_one_or_none()
        
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

        stmt = (
            select(Group)
            .where(Group.id == group_id)
            .options(selectinload(Group.accesses))
        )
        result = await self.session.execute(stmt)
        group = result.scalar_one_or_none()
        if group is None:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        stmt = select(Access).where(Access.id == access_id)
        result = await self.session.execute(stmt)
        access = result.scalar_one_or_none()
        if access is None:
            raise ValueError(f"Доступ с ID {access_id} не найден")

        if access in group.accesses:
            raise ValueError(
                f"Доступ {access_id} уже привязан к группе {group_id}"
            )

        group.accesses.append(access)
        await self.session.flush()

    async def remove_access_from_group(
        self, group_id: int, access_id: int
    ) -> None:

        stmt = (
            select(Group)
            .where(Group.id == group_id)
            .options(selectinload(Group.accesses))
        )
        result = await self.session.execute(stmt)
        group = result.scalar_one_or_none()
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
        await self.session.flush()

    async def delete_group(self, group_id: int) -> None:

        stmt = (
            select(Group)
            .where(Group.id == group_id)
            .options(
                selectinload(Group.conflicts_as_group1),
                selectinload(Group.conflicts_as_group2)
            )
        )
        result = await self.session.execute(stmt)
        group = result.scalar_one_or_none()
        if group is None:
            raise ValueError(f"Группа с ID {group_id} не найдена")

        conflicts = list(group.conflicts_as_group1) + list(group.conflicts_as_group2)
        if conflicts:
            raise ValueError(
                f"Группа с ID {group_id} не может быть удалена, так как имеет конфликты"
            )

        self.session.delete(group)
        await self.session.flush()


