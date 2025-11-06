"""
HTTP клиент для взаимодействия с Access Control Service

Получение данных о конфликтах, группах и доступах для проверки.
"""

import logging
from typing import List, Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from validation_service.services.base_client import BaseServiceClient
from validation_service.services.cache_constants import (
    CONFLICTS_MATRIX_TTL,
    GROUP_ACCESSES_TTL,
    ACCESS_GROUPS_TTL
)

logger = logging.getLogger(__name__)


class AccessControlClient(BaseServiceClient):
    """HTTP клиент для Access Control Service"""
    
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
    async def get_conflicts_matrix(
        self,
        use_cache: bool = True
    ) -> List[Dict[str, int]]:
        """Получить матрицу конфликтов между группами"""

        cache_key = "conflicts_matrix"
        
        async def fetch_conflicts():
            """Функция для получения конфликтов из API"""
            url = f"{self.base_url}/conflicts"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("conflicts", [])
        
        return await self._cached_request(
            cache_key=cache_key,
            fetch_func=fetch_conflicts,
            ttl=CONFLICTS_MATRIX_TTL,
            response_key="conflicts",
            use_cache=use_cache,
            cache_log_message="Кэш для матрицы конфликтов"
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_group_accesses(
        self,
        group_id: int,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """Получить доступы группы"""

        cache_key = f"group:{group_id}:accesses"
        
        async def fetch_accesses():
            """Функция для получения доступов группы из API"""
            url = f"{self.base_url}/groups/{group_id}/accesses"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("accesses", [])
        
        return await self._cached_request(
            cache_key=cache_key,
            fetch_func=fetch_accesses,
            ttl=GROUP_ACCESSES_TTL,
            response_key="accesses",
            use_cache=use_cache,
            cache_log_message=f"Кэш для группы {group_id} доступов"
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def get_groups_by_access(
        self,
        access_id: int,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """Получить группы, содержащие данный доступ"""

        cache_key = f"access:{access_id}:groups"
        
        async def fetch_groups():
            """Функция для получения групп по доступу из API"""
            url = f"{self.base_url}/accesses/{access_id}/groups"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("groups", [])
        
        return await self._cached_request(
            cache_key=cache_key,
            fetch_func=fetch_groups,
            ttl=ACCESS_GROUPS_TTL,
            response_key="groups",
            use_cache=use_cache,
            cache_log_message=f"Кэш для доступа {access_id} групп"
        )
    
    async def invalidate_conflicts_cache(self):
        """Инвалидировать кэш матрицы конфликтов"""
        if self.cache:
            await self.cache.delete("conflicts_matrix")
            logger.debug("Кэш инвалидирован для матрицы конфликтов")
    
    async def invalidate_group_cache(self, group_id: int):
        """Инвалидировать кэш группы"""

        if self.cache:
            cache_key = f"group:{group_id}:accesses"
            await self.cache.delete(cache_key)
            logger.debug(f"Кэш инвалидирован для группы {group_id}")
    
    async def invalidate_access_cache(self, access_id: int):
        """Инвалидировать кэш доступа"""

        if self.cache:
            cache_key = f"access:{access_id}:groups"
            await self.cache.delete(cache_key)
            logger.debug(f"Invalidated cache for access {access_id}")

