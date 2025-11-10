import logging
import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.db.database import db
from access_control_service.app.dependencies import get_redis_connection
from access_control_service.services.cache import (
    invalidate_access_groups_cache,
    invalidate_group_accesses_cache,
    invalidate_conflicts_matrix_cache
)

logger = logging.getLogger(__name__)
from access_control_service.models.models import (
    CreateResourceIn,
    CreateResourceOut,
    CreateAccessIn,
    CreateAccessOut,
    CreateGroupIn,
    CreateGroupOut,
    CreateConflictIn,
    CreateConflictOut,
    DeleteConflictIn,
    Access as AccessOut,
    AddResourceToAccessIn,
    Resource as ResourceModel,
)
from access_control_service.services.resource_service import ResourceService
from access_control_service.services.access_service import AccessService
from access_control_service.services.access_service_admin import AccessServiceAdmin
from access_control_service.services.group_service import GroupService
from access_control_service.services.conflict_service_admin import ConflictServiceAdmin
from access_control_service.app.utils.error_handlers import handle_errors

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/resources", response_model=CreateResourceOut, status_code=status.HTTP_201_CREATED)
@handle_errors(error_message_prefix="при создании ресурса")
async def create_resource(
    resource_in: CreateResourceIn,
    session: AsyncSession = Depends(db.get_db)
):
    """Создание ресурса (служебный эндпоинт)"""
    return await ResourceService.create_resource(session, resource_in)


@router.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(
    value_error_status=status.HTTP_409_CONFLICT,
    error_message_prefix="при удалении ресурса"
)
async def delete_resource(
    resource_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Удаление ресурса (служебный эндпоинт)"""
    await ResourceService.delete_resource(session, resource_id)


@router.post("/accesses", response_model=CreateAccessOut, status_code=status.HTTP_201_CREATED)
@handle_errors(error_message_prefix="при создании доступа")
async def create_access(
    access_in: CreateAccessIn,
    session: AsyncSession = Depends(db.get_db)
):
    """Создание доступа с ресурсами (служебный эндпоинт)"""
    return await AccessService.create_access(session, access_in)


@router.post("/accesses/{access_id}/resources", response_model=AccessOut)
@handle_errors(error_message_prefix="при добавлении ресурса к доступу")
async def add_resource_to_access(
    access_id: int,
    resource_data: AddResourceToAccessIn,
    session: AsyncSession = Depends(db.get_db),
    redis_conn: redis.Redis = Depends(get_redis_connection)
):
    """Добавление ресурса к доступу"""
    await AccessServiceAdmin.add_resource_to_access(
        session, access_id, resource_data.resource_id
    )
    
    # Инвалидируем кэш групп по доступу, так как изменение ресурсов доступа
    # может повлиять на группы, содержащие этот доступ
    await invalidate_access_groups_cache(redis_conn, access_id)
    
    access = await AccessService.get_access(session, access_id)
    
    resources_out = [
        ResourceModel(
            id=res.id,
            name=res.name,
            type=res.type,
            description=res.description,
        )
        for res in access.resources
    ]
    
    return AccessOut(
        id=access.id,
        name=access.name,
        resources=resources_out,
    )


@router.delete("/accesses/{access_id}/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(error_message_prefix="при удалении ресурса из доступа")
async def remove_resource_from_access(
    access_id: int,
    resource_id: int,
    session: AsyncSession = Depends(db.get_db),
    redis_conn: redis.Redis = Depends(get_redis_connection)
):
    """Удаление ресурса из доступа"""
    await AccessServiceAdmin.remove_resource_from_access(
        session, access_id, resource_id
    )
    
    # Инвалидируем кэш групп по доступу, так как изменение ресурсов доступа
    # может повлиять на группы, содержащие этот доступ
    await invalidate_access_groups_cache(redis_conn, access_id)


@router.delete("/accesses/{access_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(
    value_error_status=status.HTTP_409_CONFLICT,
    error_message_prefix="при удалении доступа"
)
async def delete_access(
    access_id: int,
    session: AsyncSession = Depends(db.get_db),
    redis_conn: redis.Redis = Depends(get_redis_connection)
):
    """Удаление доступа"""
    await AccessServiceAdmin.delete_access(session, access_id)
    
    # Инвалидируем кэш групп по доступу при удалении доступа
    await invalidate_access_groups_cache(redis_conn, access_id)



@router.post("/groups", response_model=CreateGroupOut, status_code=status.HTTP_201_CREATED)
@handle_errors(error_message_prefix="при создании группы")
async def create_group(
    group_in: CreateGroupIn,
    session: AsyncSession = Depends(db.get_db)
):
    """Создание группы прав с доступами"""
    return await GroupService.create_group(session, group_in)


@router.post("/groups/{group_id}/accesses/{access_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(error_message_prefix="при добавлении доступа к группе")
async def add_access_to_group(
    group_id: int,
    access_id: int,
    session: AsyncSession = Depends(db.get_db),
    redis_conn: redis.Redis = Depends(get_redis_connection)
):
    """Добавление доступа к группе (служебный эндпоинт)"""
    await GroupService.add_access_to_group(session, group_id, access_id)
    
    await invalidate_group_accesses_cache(redis_conn, group_id)
    await invalidate_access_groups_cache(redis_conn, access_id)


@router.delete("/groups/{group_id}/accesses/{access_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(error_message_prefix="при удалении доступа из группы")
async def remove_access_from_group(
    group_id: int,
    access_id: int,
    session: AsyncSession = Depends(db.get_db),
    redis_conn: redis.Redis = Depends(get_redis_connection)
):
    """Удаление доступа из группы (служебный эндпоинт)"""
    await GroupService.remove_access_from_group(session, group_id, access_id)
    
    await invalidate_group_accesses_cache(redis_conn, group_id)
    await invalidate_access_groups_cache(redis_conn, access_id)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(
    value_error_status=status.HTTP_409_CONFLICT,
    error_message_prefix="при удалении группы"
)
async def delete_group(
    group_id: int,
    session: AsyncSession = Depends(db.get_db),
    redis_conn: redis.Redis = Depends(get_redis_connection)
):
    """Удаление группы (служебный эндпоинт)"""
    await GroupService.delete_group(session, group_id)
    
    await invalidate_group_accesses_cache(redis_conn, group_id)


# ========== Conflicts ==========

@router.post("/conflicts", response_model=list[CreateConflictOut], status_code=status.HTTP_201_CREATED)
@handle_errors(
    value_error_status=status.HTTP_400_BAD_REQUEST,
    error_message_prefix="при создании конфликта"
)
async def create_conflict(
    conflict_in: CreateConflictIn,
    session: AsyncSession = Depends(db.get_db),
    redis_conn: redis.Redis = Depends(get_redis_connection)
):
    """Создание конфликта между группами (служебный эндпоинт).
    
    Автоматически создает симметричную пару (group1,group2) и (group2,group1)
    """
    result = await ConflictServiceAdmin.create_conflict(session, conflict_in)
    
    await invalidate_conflicts_matrix_cache(redis_conn)
    
    return result


@router.delete("/conflicts", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(error_message_prefix="при удалении конфликта")
async def delete_conflict(
    conflict_in: DeleteConflictIn,
    session: AsyncSession = Depends(db.get_db),
    redis_conn: redis.Redis = Depends(get_redis_connection)
):
    """Удаление конфликта между группами.
    
    Удаляет обе симметричные пары: (group_id1, group_id2) и (group_id2, group_id1)
    """
    await ConflictServiceAdmin.delete_conflict(session, conflict_in.group_id1, conflict_in.group_id2)
    
    await invalidate_conflicts_matrix_cache(redis_conn)

