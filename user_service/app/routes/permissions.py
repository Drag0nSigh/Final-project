import logging

from fastapi import APIRouter, HTTPException, status, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from user_service.models.models import (
    RequestAccessIn,
    RequestAccessOut,
    RevokePermissionIn,
    RevokePermissionOut,
    GetUserPermissionsOut,
    GetActiveGroupsOut,
)
from user_service.db.database import db
from user_service.app.dependencies import (
    get_settings_dependency,
    get_rabbitmq_manager_dependency,
    get_redis_connection,
)
from user_service.config.settings import Settings
from user_service.services.rabbitmq_manager import RabbitMQManager
from user_service.services.permissions_service import PermissionService
from user_service.app.utils.error_handlers import handle_errors


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/request", response_model=RequestAccessOut)
@handle_errors("Не удалось создать заявку")
async def request_access(
    request: RequestAccessIn,
    session: AsyncSession = Depends(db.get_db),
    settings: Settings = Depends(get_settings_dependency),
    rabbitmq: RabbitMQManager = Depends(get_rabbitmq_manager_dependency),
):
    """Создание заявки на получение доступа или группы прав."""

    logger.debug(
        f"Получен запрос на создание заявки: user={request.user_id} permission_type={request.permission_type} item_id={request.item_id}"
    )

    service = PermissionService(session=session)
    
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
    except Exception as exc:
        # Если публикация не удалась, логируем ошибку, но не прерываем обработку:
        # заявка уже создана в БД, её можно будет обработать позже (например, через
        # повторную публикацию или ручной запуск валидации).
        logger.exception(
            f"Не удалось опубликовать запрос на валидацию в RabbitMQ: request_id={result.request_id}"
        )

    logger.debug(f"Заявка {result.request_id} успешно принята и отправлена на валидацию")
    return result


@router.delete("/users/{user_id}/permissions", response_model=RevokePermissionOut)
@handle_errors("Не удалось отозвать право")
async def revoke_permission(
    user_id: int,
    request: RevokePermissionIn,
    session: AsyncSession = Depends(db.get_db),
    redis_conn=Depends(get_redis_connection),
):
    """Отзыв права у пользователя (синхронная операция)."""

    logger.debug(
        f"Получен запрос на отзыв права: user={user_id} permission_type={request.permission_type} item_id={request.item_id}"
    )

    service = PermissionService(session=session, redis_conn=redis_conn)
    permission = await service.revoke_permission(user_id, request.permission_type, request.item_id)

    if permission is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активное право не найдено",
        )

    logger.debug(
        f"Право отозвано: user={user_id} permission_type={request.permission_type} item_id={request.item_id}"
    )
    return RevokePermissionOut(status="revoked")


@router.get("/users/{user_id}/permissions", response_model=GetUserPermissionsOut)
@handle_errors("Не удалось получить список прав")
async def get_user_permissions(
    user_id: int,
    session: AsyncSession = Depends(db.get_db),
):
    """Получение всех прав пользователя."""

    logger.debug(f"Получение списка прав пользователя user={user_id}")

    service = PermissionService(session=session)
    return await service.get_permissions(user_id)


@router.get("/users/{user_id}/current_active_groups", response_model=GetActiveGroupsOut)
@handle_errors("Не удалось получить активные группы пользователя")
async def get_current_active_groups(
    user_id: int,
    session: AsyncSession = Depends(db.get_db),
    redis_conn=Depends(get_redis_connection),
):
    """Получение активных групп пользователя. """

    logger.debug(f"Получение активных групп пользователя user={user_id}")

    service = PermissionService(session=session, redis_conn=redis_conn)
    return await service.get_active_groups(user_id)
