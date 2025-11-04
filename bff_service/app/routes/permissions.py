from fastapi import APIRouter, Query, HTTPException, status, Path
from typing import Literal

from bff_service.models.models import (
    RequestAccessIn,
    RequestAccessOut,
    RevokePermissionIn,
    RevokePermissionOut,
    GetUserPermissionsOut,
    GetRequiredAccessOut,
    UserPermissionOut
)

router = APIRouter()


@router.post("/request", response_model=RequestAccessOut, status_code=status.HTTP_202_ACCEPTED)
async def request_access(request: RequestAccessIn):
    """
    Создание заявки на получение доступа или группы прав
    
    Проксирует запрос в User Service, который:
    - Создает запись с статусом 'pending'
    - Отправляет сообщение в RabbitMQ для асинхронной валидации
    - Возвращает request_id для отслеживания
    
    Клиент получает немедленный ответ "accepted", результат валидации придет асинхронно.
    """
    # TODO: Реализация
    # 1. Вызвать User Service API: POST /request
    # 2. Отправить сообщение в RabbitMQ validation_queue (через User Service или напрямую)
    # 3. Вернуть RequestAccessOut с request_id
    # 4. Обработать ошибки (если User Service недоступен)
    pass


@router.delete("/users/{user_id}/permissions", response_model=RevokePermissionOut)
async def revoke_permission(
    user_id: int,
    permission_type: Literal["access", "group"] = Query(..., description="Тип права: 'access' или 'group'"),
    item_id: int = Query(..., gt=0, description="ID доступа или группы")
):
    """
    Отзыв права у пользователя (синхронная операция)
    
    Проксирует запрос в User Service, который:
    - Ищет активное право по user_id, permission_type, item_id
    - Меняет статус на 'revoked'
    - Инвалидирует кэш пользователя
    """
    # TODO: Реализация
    # 1. Вызвать User Service API: DELETE /users/{user_id}/permissions?type=...&item_id=...
    # 2. Вернуть RevokePermissionOut
    # 3. Обработать ошибки (404 если право не найдено, 500 если сервис недоступен)
    pass


@router.get("/users/{user_id}/permissions", response_model=GetUserPermissionsOut)
async def get_user_permissions(user_id: int):
    """
    Получение всех прав пользователя
    
    Проксирует запрос в User Service и агрегирует данные:
    - Получает все группы прав пользователя с их доступами (nested)
    - Получает все отдельные доступы пользователя
    - Может дополнительно обогащать данными из Access Control Service
    """
    # TODO: Реализация
    # 1. Вызвать User Service API: GET /users/{user_id}/permissions
    # 2. Для каждой группы - получить nested доступы через Access Control Service API (опционально)
    # 3. Агрегировать и вернуть GetUserPermissionsOut
    # 4. Обработать ошибки
    pass


@router.get("/resources/{resource_id}/required-access", response_model=GetRequiredAccessOut)
async def get_required_access_for_resource(resource_id: int):
    """
    Получение необходимых доступов для конкретного ресурса
    
    Проксирует запрос в Access Control Service.
    Используется для определения, какие доступы нужны пользователю для работы с ресурсом.
    """
    # TODO: Реализация
    # 1. Вызвать Access Control Service API: GET /resources/{resource_id}/required_accesses
    # 2. Вернуть GetRequiredAccessOut
    # 3. Обработать ошибки (404 если ресурс не найден)
    pass


@router.get("/permissions/{request_id}", response_model=UserPermissionOut)
async def get_permission_by_request_id(
    request_id: str = Path(..., description="UUID заявки")
):
    """
    Получение информации о заявке по request_id
    
    Используется для отслеживания статуса заявки клиентом.
    Проксирует запрос в User Service.
    """
    # TODO: Реализация
    # 1. Вызвать User Service API: GET /permissions/{request_id}
    # 2. Вернуть UserPermissionOut
    # 3. Обработать ошибки (404 если заявка не найдена)
    pass

