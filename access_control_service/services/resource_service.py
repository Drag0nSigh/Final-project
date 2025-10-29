from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from access_control_service.db.resource import Resource
from access_control_service.models.models import CreateResourceIn, CreateResourceOut


class ResourceService:
    """Сервис для работы с ресурсами"""
    
    @staticmethod
    async def create_resource(session: AsyncSession, resource_data: CreateResourceIn) -> CreateResourceOut:
        """Создание ресурса"""
        # TODO: Реализация
        pass
    
    @staticmethod
    async def get_resource(session: AsyncSession, resource_id: int) -> Resource:
        """Получение ресурса по ID"""
        # TODO: Реализация
        pass
    
    @staticmethod
    async def get_all_resources(session: AsyncSession) -> list[Resource]:
        """Получение всех ресурсов"""
        # TODO: Реализация
        pass
    
    @staticmethod
    async def get_required_accesses_for_resource(session: AsyncSession, resource_id: int):
        """Получение необходимых доступов для ресурса"""
        # TODO: Реализация
        # Вернуть все Access, которые связаны с данным Resource
        pass

