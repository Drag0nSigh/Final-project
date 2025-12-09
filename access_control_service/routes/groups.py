import redis.asyncio as redis
from fastapi import APIRouter, Depends

from access_control_service.dependencies import (
    get_redis_connection,
    get_group_service,
)
from access_control_service.models.models import (
    Group as GroupOut,
    GetGroupAccessesResponse
)
from access_control_service.services.protocols import GroupServiceProtocol
from access_control_service.services.cache import (
    get_group_accesses_from_cache,
    set_group_accesses_cache
)
router = APIRouter()


@router.get("/{group_id}", response_model=GroupOut)
async def get_group(
    group_id: int,
    group_service: GroupServiceProtocol = Depends(get_group_service),
):
    group = await group_service.get_group(group_id)
    return GroupOut.model_validate(group)


@router.get("", response_model=list[GroupOut])
async def get_all_groups(
    group_service: GroupServiceProtocol = Depends(get_group_service),
):
    groups = await group_service.get_all_groups()
    return [GroupOut.model_validate(group) for group in groups]


@router.get("/{group_id}/accesses", response_model=GetGroupAccessesResponse)
async def get_accesses_by_group(
    group_id: int,
    redis_conn: redis.Redis = Depends(get_redis_connection),
    group_service: GroupServiceProtocol = Depends(get_group_service),
):
    cached_accesses = await get_group_accesses_from_cache(redis_conn, group_id)
    if cached_accesses is not None:
        return GetGroupAccessesResponse.model_validate({
            "group_id": group_id,
            "accesses": cached_accesses
        })
    
    result = await group_service.get_group_accesses(group_id)
    
    accesses_dict = [access.model_dump() for access in result.accesses]
    await set_group_accesses_cache(redis_conn, group_id, accesses_dict)
    
    return result

