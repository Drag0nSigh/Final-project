import redis.asyncio as redis
from fastapi import APIRouter, Depends

from access_control_service.dependencies import (
    get_redis_connection,
    get_conflict_service,
)
from access_control_service.models.models import GetConflictsResponse, Conflict
from access_control_service.services.protocols import ConflictServiceProtocol
from access_control_service.services.cache import (
    get_conflicts_matrix_from_cache,
    set_conflicts_matrix_cache
)

router = APIRouter()


@router.get("", response_model=GetConflictsResponse)
async def get_all_conflicts(
    redis_conn: redis.Redis = Depends(get_redis_connection),
    conflict_service: ConflictServiceProtocol = Depends(get_conflict_service),
):
    cached_conflicts = await get_conflicts_matrix_from_cache(redis_conn)
    if cached_conflicts is not None:
        conflicts = [
            Conflict.model_validate(conflict_dict)
            for conflict_dict in cached_conflicts
        ]
        return GetConflictsResponse(conflicts=conflicts)
    
    conflicts_list = await conflict_service.get_all_conflicts()
    
    conflicts_dict = [conflict.model_dump() for conflict in conflicts_list]
    await set_conflicts_matrix_cache(redis_conn, conflicts_dict)
    
    return GetConflictsResponse(conflicts=conflicts_list)

