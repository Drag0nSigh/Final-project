from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.db.access import Access
from access_control_service.models.models import CreateAccessIn, CreateAccessOut


class AccessService:
    """Сервис для работы с доступами"""
    
    @staticmethod
    async def create_access(session: AsyncSession, access_data: CreateAccessIn) -> CreateAccessOut:
        """Создание доступа"""
        # TODO: Реализация
        pass
    
    @staticmethod
    async def get_access(session: AsyncSession, access_id: int) -> Access:
        """Получение доступа по ID"""
        # TODO: Реализация
        pass
    
    @staticmethod
    async def add_resource_to_access(session: AsyncSession, access_id: int, resource_id: int):
        """Добавление ресурса к доступу"""
        # TODO: Реализация
        pass
    
    @staticmethod
    async def remove_resource_from_access(session: AsyncSession, access_id: int, resource_id: int):
        """Удаление ресурса из доступа"""
        # TODO: Реализация
        pass
    
    @staticmethod
    async def get_groups_containing_access(session: AsyncSession, access_id: int):
        """Получение групп, содержащих данный доступ"""
        # TODO: Реализация
        # Вернуть все Group, которые содержат данный Access
        pass

