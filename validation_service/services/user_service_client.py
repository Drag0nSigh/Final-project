"""
HTTP клиент для взаимодействия с User Service

Получение данных о пользователях и их правах для проверки конфликтов.
"""

import logging
from typing import List, Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from validation_service.services.base_client import BaseServiceClient
from validation_service.services.cache_constants import USER_GROUPS_TTL

logger = logging.getLogger(__name__)


class UserServiceClient(BaseServiceClient):
    """HTTP клиент для User Service"""
    
    def __init__(
        self,
        base_url: str,
        cache: Optional[Any] = None,
        timeout: float = 30.0
    ):
        """Инициализация клиента"""
        super().__init__(base_url, cache, timeout)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_user_active_groups(
        self,
        user_id: int,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """Получить активные группы пользователя"""

        cache_key = f"user:{user_id}:groups"
        
        async def fetch_groups():
            """Функция для получения групп из API"""
            url = f"{self.base_url}/users/{user_id}/current_active_groups"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("groups", [])
        
        return await self._cached_request(
            cache_key=cache_key,
            fetch_func=fetch_groups,
            ttl=USER_GROUPS_TTL,
            response_key="groups",
            use_cache=use_cache,
            cache_log_message=f"Кэш для пользователя {user_id} групп"
        )
    
    async def invalidate_user_cache(self, user_id: int):
        """Инвалидировать кэш пользователя"""

        if self.cache:
            cache_key = f"user:{user_id}:groups"
            await self.cache.delete(cache_key)
            logger.debug(f"Invalidated cache for user {user_id}")

