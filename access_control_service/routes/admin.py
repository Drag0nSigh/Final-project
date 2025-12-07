import logging
import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, status

from access_control_service.dependencies import (
    get_redis_connection,
    get_resource_service,
    get_access_service,
    get_access_service_admin,
    get_group_service,
    get_conflict_service_admin,
)
from access_control_service.services.cache import (
    invalidate_access_groups_cache,
    invalidate_group_accesses_cache,
    invalidate_conflicts_matrix_cache
)
from access_control_service.services.protocols import (
    ResourceServiceProtocol,
    AccessServiceProtocol,
    AccessServiceAdminProtocol,
    GroupServiceProtocol,
    ConflictServiceAdminProtocol,
)

logger = logging.getLogger(__name__)
from access_control_service.models.models import (
    CreateResourceRequest,
    CreateResourceResponse,
    CreateAccessRequest,
    CreateAccessResponse,
    CreateGroupRequest,
    CreateGroupResponse,
    CreateConflictRequest,
    CreateConflictResponse,
    DeleteConflictRequest,
    Access as AccessOut,
    AddResourceToAccessRequest,
    Resource as ResourceModel,
)
from access_control_service.utils.error_handlers import handle_errors

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/resources", response_model=CreateResourceResponse, status_code=status.HTTP_201_CREATED)
@handle_errors(error_message_prefix="при создании ресурса")
async def create_resource(
    resource_in: CreateResourceRequest,
    resource_service: ResourceServiceProtocol = Depends(get_resource_service),
):
    return await resource_service.create_resource(resource_in)


@router.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(
    value_error_status=status.HTTP_409_CONFLICT,
    error_message_prefix="при удалении ресурса"
)
async def delete_resource(
    resource_id: int,
    resource_service: ResourceServiceProtocol = Depends(get_resource_service),
):
    await resource_service.delete_resource(resource_id)


@router.post("/accesses", response_model=CreateAccessResponse, status_code=status.HTTP_201_CREATED)
@handle_errors(error_message_prefix="при создании доступа")
async def create_access(
    access_in: CreateAccessRequest,
    access_service: AccessServiceProtocol = Depends(get_access_service),
):
    return await access_service.create_access(access_in)


@router.post("/accesses/{access_id}/resources", response_model=AccessOut)
@handle_errors(error_message_prefix="при добавлении ресурса к доступу")
async def add_resource_to_access(
    access_id: int,
    resource_data: AddResourceToAccessRequest,
    redis_conn: redis.Redis = Depends(get_redis_connection),
    access_service_admin: AccessServiceAdminProtocol = Depends(get_access_service_admin),
    access_service: AccessServiceProtocol = Depends(get_access_service),
):
    await access_service_admin.add_resource_to_access(
        access_id, resource_data.resource_id
    )
    
    await invalidate_access_groups_cache(redis_conn, access_id)
    
    access = await access_service.get_access(access_id)
    
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
    redis_conn: redis.Redis = Depends(get_redis_connection),
    access_service_admin: AccessServiceAdminProtocol = Depends(get_access_service_admin),
):
    await access_service_admin.remove_resource_from_access(
        access_id, resource_id
    )
    
    await invalidate_access_groups_cache(redis_conn, access_id)


@router.delete("/accesses/{access_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(
    value_error_status=status.HTTP_409_CONFLICT,
    error_message_prefix="при удалении доступа"
)
async def delete_access(
    access_id: int,
    redis_conn: redis.Redis = Depends(get_redis_connection),
    access_service_admin: AccessServiceAdminProtocol = Depends(get_access_service_admin),
):
    await access_service_admin.delete_access(access_id)
    
    await invalidate_access_groups_cache(redis_conn, access_id)


@router.post("/groups", response_model=CreateGroupResponse, status_code=status.HTTP_201_CREATED)
@handle_errors(error_message_prefix="при создании группы")
async def create_group(
    group_in: CreateGroupRequest,
    group_service: GroupServiceProtocol = Depends(get_group_service),
):
    return await group_service.create_group(group_in)


@router.post("/groups/{group_id}/accesses/{access_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(error_message_prefix="при добавлении доступа к группе")
async def add_access_to_group(
    group_id: int,
    access_id: int,
    redis_conn: redis.Redis = Depends(get_redis_connection),
    group_service: GroupServiceProtocol = Depends(get_group_service),
):
    await group_service.add_access_to_group(group_id, access_id)
    
    await invalidate_group_accesses_cache(redis_conn, group_id)
    await invalidate_access_groups_cache(redis_conn, access_id)


@router.delete("/groups/{group_id}/accesses/{access_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(error_message_prefix="при удалении доступа из группы")
async def remove_access_from_group(
    group_id: int,
    access_id: int,
    redis_conn: redis.Redis = Depends(get_redis_connection),
    group_service: GroupServiceProtocol = Depends(get_group_service),
):
    await group_service.remove_access_from_group(group_id, access_id)
    
    await invalidate_group_accesses_cache(redis_conn, group_id)
    await invalidate_access_groups_cache(redis_conn, access_id)


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(
    value_error_status=status.HTTP_409_CONFLICT,
    error_message_prefix="при удалении группы"
)
async def delete_group(
    group_id: int,
    redis_conn: redis.Redis = Depends(get_redis_connection),
    group_service: GroupServiceProtocol = Depends(get_group_service),
):
    await group_service.delete_group(group_id)
    
    await invalidate_group_accesses_cache(redis_conn, group_id)


@router.post("/conflicts", response_model=list[CreateConflictResponse], status_code=status.HTTP_201_CREATED)
@handle_errors(
    value_error_status=status.HTTP_400_BAD_REQUEST,
    error_message_prefix="при создании конфликта"
)
async def create_conflict(
    conflict_in: CreateConflictRequest,
    redis_conn: redis.Redis = Depends(get_redis_connection),
    conflict_service_admin: ConflictServiceAdminProtocol = Depends(get_conflict_service_admin),
):
    """Создание конфликта между группами (служебный эндпоинт).
    
    Автоматически создает симметричную пару (group1,group2) и (group2,group1)
    """
    result = await conflict_service_admin.create_conflict(conflict_in)
    
    await invalidate_conflicts_matrix_cache(redis_conn)
    
    return result


@router.delete("/conflicts", status_code=status.HTTP_204_NO_CONTENT)
@handle_errors(error_message_prefix="при удалении конфликта")
async def delete_conflict(
    conflict_in: DeleteConflictRequest,
    redis_conn: redis.Redis = Depends(get_redis_connection),
    conflict_service_admin: ConflictServiceAdminProtocol = Depends(get_conflict_service_admin),
):
    """Удаление конфликта между группами.
    
    Удаляет обе симметричные пары: (group_id1, group_id2) и (group_id2, group_id1)
    """
    await conflict_service_admin.delete_conflict(conflict_in.group_id1, conflict_in.group_id2)
    
    await invalidate_conflicts_matrix_cache(redis_conn)

