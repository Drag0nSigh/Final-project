import logging
import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.app.dependencies import get_db_session
from access_control_service.app.dependencies import get_redis_connection
from access_control_service.models.models import GetConflictsResponse, Conflict
from access_control_service.services.conflict_service import ConflictService
from access_control_service.services.cache import (
    get_conflicts_matrix_from_cache,
    set_conflicts_matrix_cache
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=GetConflictsResponse)
async def get_all_conflicts(
    session: AsyncSession = Depends(get_db_session),
    redis_conn: redis.Redis = Depends(get_redis_connection)
):
    """Получение всех конфликтов"""
    try:
        cached_conflicts = await get_conflicts_matrix_from_cache(redis_conn)
        if cached_conflicts is not None:
            conflicts = [
                Conflict.model_validate(conflict_dict)
                for conflict_dict in cached_conflicts
            ]
            return GetConflictsResponse(conflicts=conflicts)
        
        conflicts_list = await ConflictService.get_all_conflicts(session)
        
        conflicts_dict = [conflict.model_dump() for conflict in conflicts_list]
        await set_conflicts_matrix_cache(redis_conn, conflicts_dict)
        
        return GetConflictsResponse(conflicts=conflicts_list)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении конфликтов: {str(exc)}"
        )

