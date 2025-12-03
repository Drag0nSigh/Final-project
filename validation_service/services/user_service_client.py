import logging
from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential

from validation_service.services.base_client import BaseServiceClient
from validation_service.services.cache_constants import USER_GROUPS_TTL

logger = logging.getLogger(__name__)


class UserServiceClient(BaseServiceClient):
    """HTTP клиент для User Service"""
    
    def __init__(
        self,
        base_url: str,
        cache: Any | None = None,
        timeout: float = 30.0
    ):
        """Инициализация клиента"""
        super().__init__(base_url, cache, timeout)
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=10)
    )
    async def get_user_active_groups(
        self,
        user_id: int,
        use_cache: bool = True
    ) -> list[dict[str, Any]]:
        """Получить активные группы пользователя"""

        cache_key = f"user:{user_id}:groups"
        
        cached = await self._get_from_cache(
            cache_key=cache_key,
            response_key="groups",
            use_cache=use_cache,
            cache_log_message=f"Кэш для пользователя {user_id} групп"
        )
        if cached is not None:
            return cached
        
        data = await self._get_json_data(f"users/{user_id}/current_active_groups", response_key="groups")
        
        await self._set_to_cache(
            cache_key=cache_key,
            data=data,
            response_key="groups",
            ttl=USER_GROUPS_TTL,
            use_cache=use_cache,
            cache_log_message=f"Кэш сохранен для пользователя {user_id} групп"
        )
        
        return data
    
    async def invalidate_user_cache(self, user_id: int):
        """Инвалидировать кэш пользователя"""
        await self._invalidate_cache(
            f"user:{user_id}:groups",
            f"Кэш инвалидирован для пользователя {user_id}"
        )

