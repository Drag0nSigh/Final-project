import logging
from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential

from validation_service.services.base_client import BaseServiceClient
from validation_service.services.cache_constants import USER_GROUPS_TTL
from validation_service.models.service_models import GetUserGroupsResponse, Group

logger = logging.getLogger(__name__)


class UserServiceClient(BaseServiceClient):
    
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
    async def get_user_active_groups(
        self,
        user_id: int,
        use_cache: bool = True
    ) -> GetUserGroupsResponse:

        cache_key = f"user:{user_id}:groups"
        
        cached = await self._get_from_cache(
            cache_key=cache_key,
            response_key="groups",
            use_cache=use_cache,
            cache_log_message=f"Кэш для пользователя {user_id} групп"
        )
        if cached is not None:
            groups = [Group.model_validate(group_dict) for group_dict in cached]
            return GetUserGroupsResponse(groups=groups)
        
        data = await self._get_json_data(f"users/{user_id}/current_active_groups", response_key="groups")
        
        groups = [Group.model_validate(group_dict) for group_dict in data]
        response = GetUserGroupsResponse(groups=groups)
        
        groups_dict = [group.model_dump() for group in groups]
        await self._set_to_cache(
            cache_key=cache_key,
            data=groups_dict,
            response_key="groups",
            ttl=USER_GROUPS_TTL,
            use_cache=use_cache,
            cache_log_message=f"Кэш сохранен для пользователя {user_id} групп"
        )
        
        return response
    
    async def invalidate_user_cache(self, user_id: int):
        await self._invalidate_cache(
            f"user:{user_id}:groups",
            f"Кэш инвалидирован для пользователя {user_id}"
        )

