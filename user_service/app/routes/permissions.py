import logging

from fastapi import APIRouter, Query, HTTPException, status, Path, Depends
from typing import Literal
from uuid import uuid4

from sqlalchemy import select
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
from user_service.db.userpermission import UserPermission
from user_service.app.dependencies import (
    get_settings_dependency,
    get_rabbitmq_manager_dependency,
    get_redis_connection,
)
from user_service.config.settings import Settings
from user_service.services.rabbitmq_manager import RabbitMQManager
from user_service.services.permissions_service import PermissionService


logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/request", response_model=RequestAccessOut)
async def request_access(
    request: RequestAccessIn,
    session: AsyncSession = Depends(db.get_db),
    settings: Settings = Depends(get_settings_dependency),
    rabbitmq: RabbitMQManager = Depends(get_rabbitmq_manager_dependency),
):
    """Создание заявки на получение доступа или группы прав.

    ***ВАЖНО для BFF Service***: Этот эндпоинт вызывается BFF при создании заявки.
    Формат запроса: ``RequestAccessIn`` с полями ``user_id`` (int), ``permission_type``
    (Literal["access", "group"]), ``item_id`` (int). Формат ответа: ``RequestAccessOut``
    с полями ``status="accepted"`` и ``request_id`` (UUID строка). Эндпоинт возвращает
    ответ немедленно, не дожидаясь результата валидации (асинхронная обработка)."""

    logger.info(
        "Получен запрос на создание заявки: user=%s permission_type=%s item_id=%s",
        request.user_id,
        request.permission_type,
        request.item_id,
    )

    try:
        stmt = select(UserPermission).where(
            UserPermission.user_id == request.user_id,
            UserPermission.permission_type == request.permission_type,
            UserPermission.item_id == request.item_id,
        )
        result = await session.execute(stmt)
        existing_permission = result.scalar_one_or_none()

        if existing_permission and existing_permission.status in {"active", "pending"}:
            logger.warning(
                "Заявка отклонена: уже существует запись со статусом %s",
                existing_permission.status,
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Заявка уже находится в обработке или право активно",
            )

        new_request_id = str(uuid4())

        if existing_permission and existing_permission.status in {"revoked", "rejected"}:
            existing_permission.status = "pending"
            existing_permission.request_id = new_request_id
            existing_permission.assigned_at = None
            permission_record = existing_permission
            logger.info(
                "Повторное использование заявки %s: статус переведён в pending",
                new_request_id,
            )
        else:
            permission_record = UserPermission(
                user_id=request.user_id,
                permission_type=request.permission_type,
                item_id=request.item_id,
                item_name=None,
                status="pending",
                request_id=new_request_id,
                assigned_at=None,
            )
            session.add(permission_record)
            logger.info("Создана новая заявка %s", new_request_id)

        await session.flush()

        try:
            await rabbitmq.publish_validation_request(
                user_id=request.user_id,
                permission_type=request.permission_type,
                item_id=request.item_id,
                request_id=new_request_id,
            )
        except Exception as exc:
            # Если публикация не удалась, логируем ошибку, но не прерываем обработку:
            # заявка уже создана в БД, её можно будет обработать позже (например, через
            # повторную публикацию или ручной запуск валидации).
            logger.exception(
                "Не удалось опубликовать запрос на валидацию в RabbitMQ: request_id=%s",
                new_request_id,
            )

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - защитный код
        logger.exception("Ошибка при создании заявки")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать заявку",
        ) from exc

    logger.info("Заявка %s успешно принята и отправлена на валидацию", new_request_id)
    return RequestAccessOut(status="accepted", request_id=new_request_id)


@router.delete("/users/{user_id}/permissions", response_model=RevokePermissionOut)
async def revoke_permission(
    user_id: int,
    permission_type: Literal["access", "group"] = Query(..., description="Тип права: 'access' или 'group'"),
    item_id: int = Query(..., gt=0, description="ID доступа или группы"),
    session: AsyncSession = Depends(db.get_db),
    redis_conn=Depends(get_redis_connection),
):
    """Отзыв права у пользователя (синхронная операция).

    ***ВАЖНО для BFF Service***: Этот эндпоинт вызывается BFF при отзыве права.
    Формат запроса: ``DELETE /users/{user_id}/permissions?permission_type={access|group}&item_id={int}``.
    Формат ответа: ``RevokePermissionOut`` с полем ``status="revoked"``. Если право не найдено,
    возвращается 404. Если право успешно отозвано, возвращается 200."""

    logger.info(
        "Получен запрос на отзыв права: user=%s permission_type=%s item_id=%s",
        user_id,
        permission_type,
        item_id,
    )

    try:
        service = PermissionService(session=session, redis_conn=redis_conn)
        permission = await service.revoke_permission(user_id, permission_type, item_id)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        logger.exception("Ошибка при попытке отозвать право")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось отозвать право",
        ) from exc

    if permission is None:
        logger.warning(
            "Право не найдено: user=%s permission_type=%s item_id=%s",
            user_id,
            permission_type,
            item_id,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Активное право не найдено",
        )

    logger.info(
        "Право отозвано: user=%s permission_type=%s item_id=%s",
        user_id,
        permission_type,
        item_id,
    )
    return RevokePermissionOut(status="revoked")


@router.get("/users/{user_id}/permissions", response_model=GetUserPermissionsOut)
async def get_user_permissions(
    user_id: int,
    session: AsyncSession = Depends(db.get_db),
):
    """Получение всех прав пользователя.

    ***ВАЖНО для BFF Service***: Этот эндпоинт вызывается BFF для получения всех прав пользователя.
    Формат запроса: ``GET /users/{user_id}/permissions``.
    Формат ответа: ``GetUserPermissionsOut`` с полями ``user_id`` (int), ``groups`` (list[PermissionOut]),
    ``accesses`` (list[PermissionOut]). Каждый ``PermissionOut`` содержит: ``id``, ``permission_type``,
    ``item_id``, ``item_name`` (опционально), ``status``, ``assigned_at`` (опционально).

    ***ВАЖНО для Access Control Service***: В будущем этот эндпоинт будет обогащаться данными из
    Access Control Service (детали доступов и групп). BFF может использовать этот эндпоинт для
    агрегации данных от User Service и Access Control Service.

    На текущем этапе возвращаем содержимое таблицы ``user_permissions`` без
    вложенных деталей. Позднее добавим вытягивание информации из Access Control
    Service и обогащение ответа вложенными доступами.
    """

    logger.debug("Получение списка прав пользователя user=%s", user_id)

    try:
        service = PermissionService(session=session)
        return await service.get_permissions(user_id)
    except Exception as exc:  # pragma: no cover
        logger.exception("Ошибка при получении прав пользователя")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить список прав",
        ) from exc


@router.get("/users/{user_id}/current_active_groups", response_model=GetActiveGroupsOut)
async def get_current_active_groups(
    user_id: int,
    session: AsyncSession = Depends(db.get_db),
    redis_conn=Depends(get_redis_connection),
):
    """Получение активных групп пользователя (для Validation Service).

    ***ВАЖНО для Validation Service***: Этот эндпоинт вызывается Validation Service при проверке
    конфликтов. Формат запроса: ``GET /users/{user_id}/current_active_groups``.
    Формат ответа: ``GetActiveGroupsOut`` с полем ``groups`` (list[ActiveGroup]), где каждый
    ``ActiveGroup`` содержит ``id`` (int) и ``name`` (Optional[str]). Возвращаются только группы
    со статусом ``active``. Используется кэш Redis для ускорения запросов.

    Метод отдаёт Pydantic-схему ``GetActiveGroupsOut``. Основная часть логики
    вынесена в ``PermissionService``: там происходит работа с Redis и БД. Здесь
    лишь передаём зависимостям корректные аргументы.
    """

    logger.debug("Получение активных групп пользователя user=%s", user_id)

    try:
        service = PermissionService(session=session, redis_conn=redis_conn)
        return await service.get_active_groups(user_id)
    except Exception as exc:  # pragma: no cover
        logger.exception("Ошибка при получении активных групп пользователя")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить активные группы пользователя",
        ) from exc
