import logging
from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential

from validation_service.services.base_client import BaseServiceClient
from validation_service.services.cache_constants import (
    CONFLICTS_MATRIX_TTL,
    GROUP_ACCESSES_TTL,
    ACCESS_GROUPS_TTL
)
from validation_service.models.service_models import (
    GetConflictsResponse,
    GetGroupAccessesResponse,
    GetAccessGroupsResponse,
    Conflict,
    Access,
    Group,
)

logger = logging.getLogger(__name__)


class AccessControlClient(BaseServiceClient):
    
    def __init__(
        self,
        base_url: str,
        cache: Any | None = None,
        timeout: float = 30.0
    ):
        super().__init__(base_url, cache, timeout)
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=10)
    )
    async def get_conflicts_matrix(
        self,
        use_cache: bool = True
    ) -> GetConflictsResponse:

        cache_key = "conflicts_matrix"
        
        cached = await self._get_from_cache(
            cache_key=cache_key,
            response_key="conflicts",
            use_cache=use_cache,
            cache_log_message="Кэш для матрицы конфликтов"
        )
        if cached is not None:
            conflicts = [Conflict.model_validate(conflict_dict) for conflict_dict in cached]
            return GetConflictsResponse(conflicts=conflicts)
        
        data = await self._get_json_data("conflicts", response_key="conflicts")
        
        conflicts = [Conflict.model_validate(conflict_dict) for conflict_dict in data]
        response = GetConflictsResponse(conflicts=conflicts)
        
        conflicts_dict = [conflict.model_dump() for conflict in conflicts]
        await self._set_to_cache(
            cache_key=cache_key,
            data=conflicts_dict,
            response_key="conflicts",
            ttl=CONFLICTS_MATRIX_TTL,
            use_cache=use_cache,
            cache_log_message="Кэш сохранен для матрицы конфликтов"
        )
        
        return response
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=10)
    )
    async def get_group_accesses(
        self,
        group_id: int,
        use_cache: bool = True
    ) -> GetGroupAccessesResponse:

        cache_key = f"group:{group_id}:accesses"
        
        cached = await self._get_from_cache(
            cache_key=cache_key,
            response_key="accesses",
            use_cache=use_cache,
            cache_log_message=f"Кэш для группы {group_id} доступов"
        )
        if cached is not None:
            accesses = [Access.model_validate(access_dict) for access_dict in cached]
            return GetGroupAccessesResponse(group_id=group_id, accesses=accesses)
        
        response_data = await self._get_json_data(f"groups/{group_id}/accesses", response_key="accesses")
        
        accesses = [Access.model_validate(access_dict) for access_dict in response_data]
        response = GetGroupAccessesResponse(group_id=group_id, accesses=accesses)
        
        accesses_dict = [access.model_dump() for access in response.accesses]
        await self._set_to_cache(
            cache_key=cache_key,
            data=accesses_dict,
            response_key="accesses",
            ttl=GROUP_ACCESSES_TTL,
            use_cache=use_cache,
            cache_log_message=f"Кэш сохранен для группы {group_id} доступов"
        )
        
        return response
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=10)
    )
    async def get_groups_by_access(
        self,
        access_id: int,
        use_cache: bool = True
    ) -> GetAccessGroupsResponse:

        cache_key = f"access:{access_id}:groups"
        
        cached = await self._get_from_cache(
            cache_key=cache_key,
            response_key="groups",
            use_cache=use_cache,
            cache_log_message=f"Кэш для доступа {access_id} групп"
        )
        if cached is not None:
            groups = [Group.model_validate(group_dict) for group_dict in cached]
            return GetAccessGroupsResponse(access_id=access_id, groups=groups)
        
        response_data = await self._get_json_data(f"accesses/{access_id}/groups", response_key="groups")
        
        groups = [Group.model_validate(group_dict) for group_dict in response_data]
        response = GetAccessGroupsResponse(access_id=access_id, groups=groups)
        
        groups_dict = [group.model_dump() for group in response.groups]
        await self._set_to_cache(
            cache_key=cache_key,
            data=groups_dict,
            response_key="groups",
            ttl=ACCESS_GROUPS_TTL,
            use_cache=use_cache,
            cache_log_message=f"Кэш сохранен для доступа {access_id} групп"
        )
        
        return response
    
    async def invalidate_conflicts_cache(self):
        await self._invalidate_cache(
            "conflicts_matrix",
            "Кэш инвалидирован для матрицы конфликтов"
        )
    
    async def invalidate_group_cache(self, group_id: int):
        await self._invalidate_cache(
            f"group:{group_id}:accesses",
            f"Кэш инвалидирован для группы {group_id}"
        )
    
    async def invalidate_access_cache(self, access_id: int):
        await self._invalidate_cache(
            f"access:{access_id}:groups",
            f"Кэш инвалидирован для доступа {access_id}"
        )

