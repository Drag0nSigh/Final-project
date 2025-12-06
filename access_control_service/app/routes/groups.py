import redis.asyncio as redis
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.app.dependencies import get_db_session
from access_control_service.app.dependencies import get_redis_connection
from access_control_service.models.models import (
    Group as GroupOut,
    GetGroupAccessesOut
)
from access_control_service.services.group_service import GroupService
from access_control_service.services.cache import (
    get_group_accesses_from_cache,
    set_group_accesses_cache
)
from access_control_service.app.utils.error_handlers import handle_errors

router = APIRouter()


@router.get("/{group_id}", response_model=GroupOut)
@handle_errors(error_message_prefix="при получении группы")
async def get_group(
    group_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение группы по ID"""
    group = await GroupService.get_group(session, group_id)
    return GroupOut.model_validate(group)


@router.get("", response_model=list[GroupOut])
@handle_errors(error_message_prefix="при получении всех групп")
async def get_all_groups(
    session: AsyncSession = Depends(get_db_session)
):
    """Получение всех групп"""
    groups = await GroupService.get_all_groups(session)
    return [GroupOut.model_validate(group) for group in groups]


@router.get("/{group_id}/accesses", response_model=GetGroupAccessesOut)
@handle_errors(error_message_prefix="при получении доступов группы")
async def get_accesses_by_group(
    group_id: int,
    session: AsyncSession = Depends(get_db_session),
    redis_conn: redis.Redis = Depends(get_redis_connection)
):
    """Получение доступов группы"""
    cached_accesses = await get_group_accesses_from_cache(redis_conn, group_id)
    if cached_accesses is not None:
        return GetGroupAccessesOut.model_validate({
            "group_id": group_id,
            "accesses": cached_accesses
        })
    
    result = await GroupService.get_group_accesses(session, group_id)
    
    accesses_dict = [access.model_dump() for access in result.accesses]
    await set_group_accesses_cache(redis_conn, group_id, accesses_dict)
    
    return result

