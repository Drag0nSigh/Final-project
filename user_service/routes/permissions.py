import logging

from fastapi import APIRouter, HTTPException, status, Depends

from user_service.models.models import (
    RequestAccessRequest,
    RequestAccessResponse,
    RevokePermissionRequest,
    RevokePermissionResponse,
    GetUserPermissionsResponse,
    GetActiveGroupsResponse,
)
from user_service.dependencies import (
    get_settings_dependency,
    get_rabbitmq_manager_dependency,
    get_permission_service,
)
from user_service.config.settings import Settings
from user_service.db.protocols import RabbitMQManagerProtocol, PermissionServiceProtocol


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/request", response_model=RequestAccessResponse)
async def request_access(
    request: RequestAccessRequest,
    service: PermissionServiceProtocol = Depends(get_permission_service),
    settings: Settings = Depends(get_settings_dependency),
    rabbitmq: RabbitMQManagerProtocol = Depends(get_rabbitmq_manager_dependency),
):
    logger.debug(
        f"Получен запрос на создание заявки: user={request.user_id} permission_type={request.permission_type} item_id={request.item_id}"
    )

    try:
        result = await service.create_request(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    try:
        await rabbitmq.publish_validation_request(
            user_id=request.user_id,
            permission_type=request.permission_type,
            item_id=request.item_id,
            request_id=result.request_id,
        )
    except Exception:
        # Если публикация не удалась, логируем ошибку, но не прерываем обработку:
        # заявка уже создана в БД, её можно будет обработать позже (например, через
        # повторную публикацию или ручной запуск валидации).
        logger.exception(
            f"Не удалось опубликовать запрос на валидацию в RabbitMQ: request_id={result.request_id}"
        )

    logger.debug(f"Заявка {result.request_id} успешно принята и отправлена на валидацию")
    return result


@router.delete("/users/{user_id}/permissions", response_model=RevokePermissionResponse)
async def revoke_permission(
    user_id: int,
    request: RevokePermissionRequest,
    service: PermissionServiceProtocol = Depends(get_permission_service),
):
    logger.debug(
        f"Получен запрос на отзыв права: user={user_id} permission_type={request.permission_type} item_id={request.item_id}"
    )

    permission = await service.revoke_permission(user_id, request.permission_type, request.item_id)

    if permission is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активное право не найдено",
        )

    logger.debug(
        f"Право отозвано: user={user_id} permission_type={request.permission_type} item_id={request.item_id}"
    )
    return RevokePermissionResponse(status="revoked")


@router.get("/users/{user_id}/permissions", response_model=GetUserPermissionsResponse)
async def get_user_permissions(
    user_id: int,
    service: PermissionServiceProtocol = Depends(get_permission_service),
):
    logger.debug(f"Получение списка прав пользователя user={user_id}")

    return await service.get_permissions(user_id)


@router.get("/users/{user_id}/current_active_groups", response_model=GetActiveGroupsResponse)
async def get_current_active_groups(
    user_id: int,
    service: PermissionServiceProtocol = Depends(get_permission_service),
):
    logger.debug(f"Получение активных групп пользователя user={user_id}")

    return await service.get_active_groups(user_id)
