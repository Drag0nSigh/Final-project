from fastapi import APIRouter, Query, HTTPException, status
from typing import Literal

from user_service.models.models import (
    RequestAccessIn,
    RequestAccessOut,
    RevokePermissionIn,
    RevokePermissionOut,
    GetUserPermissionsOut,
    GetActiveGroupsOut
)

router = APIRouter()


@router.post("/request", response_model=RequestAccessOut)
async def request_access(request: RequestAccessIn):
    """
    Создание заявки на получение доступа или группы прав
    
    - Создает запись с статусом 'pending'
    - Отправляет сообщение в RabbitMQ для асинхронной валидации
    - Возвращает request_id для отслеживания
    """
    # TODO: Реализация
    # 1. Проверить, не существует ли уже такая заявка/право
    # 2. Создать UserPermission с status='pending'
    # 3. Сгенерировать UUID для request_id
    # 4. Отправить сообщение в RabbitMQ (validation_queue)
    # 5. Вернуть RequestAccessOut
    pass


@router.delete("/users/{user_id}/permissions", response_model=RevokePermissionOut)
async def revoke_permission(
    user_id: int,
    permission_type: Literal["access", "group"] = Query(..., description="Тип права: 'access' или 'group'"),
    item_id: int = Query(..., gt=0, description="ID доступа или группы")
):
    """
    Отзыв права у пользователя (синхронная операция)
    
    - Ищет активное право по user_id, permission_type, item_id
    - Меняет статус на 'revoked'
    - Инвалидирует кэш пользователя
    """
    
    # TODO: Реализация
    # 1. Найти UserPermission с status='active'
    # 2. Если не найдено - raise HTTPException(status_code=404)
    # 3. Установить status='revoked'
    # 4. Инвалидировать кэш Redis (user:{user_id}:groups)
    # 5. Вернуть RevokePermissionOut
    pass


@router.get("/users/{user_id}/permissions", response_model=GetUserPermissionsOut)
async def get_user_permissions(user_id: int):
    """
    Получение всех прав пользователя
    
    Возвращает:
    - Все группы прав пользователя с их доступами (nested)
    - Все отдельные доступы пользователя
    """
    # TODO: Реализация
    # 1. Получить все UserPermission для user_id (всех типов и статусов, кроме revoked?)
    # 2. Разделить на groups и accesses
    # 3. Для групп - получить nested доступы через Access Control Service API
    # 4. Вернуть GetUserPermissionsOut
    pass


@router.get("/users/{user_id}/current_active_groups", response_model=GetActiveGroupsOut)
async def get_current_active_groups(user_id: int):
    """
    Получение активных групп пользователя (для Validation Service)
    
    Возвращает только активные группы (status='active', permission_type='group')
    Используется Validation Service для проверки конфликтов
    """
    # TODO: Реализация
    # 1. Получить все UserPermission для user_id где:
    #    - permission_type='group'
    #    - status='active'
    # 2. Вернуть список групп в формате GetActiveGroupsOut
    # 3. Можно использовать кэш Redis
    pass

