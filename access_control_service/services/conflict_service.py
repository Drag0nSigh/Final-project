from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.db.conflict import Conflict
from access_control_service.models.models import CreateConflictIn, CreateConflictOut


class ConflictService:
    """Сервис для работы с конфликтами между группами"""
    
    @staticmethod
    async def create_conflict(session: AsyncSession, conflict_data: CreateConflictIn) -> CreateConflictOut:
        """Создание конфликта между группами (с автоматической симметрией)"""
        # TODO: Реализация
        # При создании конфликта (group_id1, group_id2) нужно создать обе пары:
        # (group_id1, group_id2) и (group_id2, group_id1) если их еще нет
        pass
    
    @staticmethod
    async def get_all_conflicts(session: AsyncSession) -> list[Conflict]:
        """Получение всех конфликтов"""
        # TODO: Реализация
        # Вернуть список всех конфликтов для кэширования в Validation Service
        pass
    
    @staticmethod
    async def get_conflicts_for_group(session: AsyncSession, group_id: int) -> list[Conflict]:
        """Получение всех конфликтов для конкретной группы"""
        # TODO: Реализация
        # Вернуть конфликты где group_id1 == group_id или group_id2 == group_id
        pass

