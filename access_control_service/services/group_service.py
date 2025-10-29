from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.db.group import Group
from access_control_service.models.models import CreateGroupIn, CreateGroupOut


class GroupService:
    """Сервис для работы с группами прав"""
    
    @staticmethod
    async def create_group(session: AsyncSession, group_data: CreateGroupIn) -> CreateGroupOut:
        """Создание группы прав"""
        # TODO: Реализация
        pass
    
    @staticmethod
    async def get_group(session: AsyncSession, group_id: int) -> Group:
        """Получение группы по ID"""
        # TODO: Реализация
        pass
    
    @staticmethod
    async def get_all_groups(session: AsyncSession) -> list[Group]:
        """Получение всех групп"""
        # TODO: Реализация
        pass
    
    @staticmethod
    async def get_group_accesses(session: AsyncSession, group_id: int):
        """Получение всех доступов группы"""
        # TODO: Реализация
        # Вернуть все Access, связанные с данной Group
        pass

