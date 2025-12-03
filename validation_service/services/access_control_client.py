import logging
from typing import Any
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
        cache: Any | None = None,
        timeout: float = 30.0
    ):
        """Инициализация клиента"""
        super().__init__(base_url, cache, timeout)
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=10)
    )
    async def get_conflicts_matrix(
        self,
        use_cache: bool = True
    ) -> list[dict[str, int]]:
        """Получить матрицу конфликтов между группами"""

        cache_key = "conflicts_matrix"
        
        cached = await self._get_from_cache(
            cache_key=cache_key,
            response_key="conflicts",
            use_cache=use_cache,
            cache_log_message="Кэш для матрицы конфликтов"
        )
        if cached is not None:
            return cached
        
        data = await self._get_json_data("conflicts", response_key="conflicts")
        
        await self._set_to_cache(
            cache_key=cache_key,
            data=data,
            response_key="conflicts",
            ttl=CONFLICTS_MATRIX_TTL,
            use_cache=use_cache,
            cache_log_message="Кэш сохранен для матрицы конфликтов"
        )
        
        return data
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=10)
    )
    async def get_group_accesses(
        self,
        group_id: int,
        use_cache: bool = True
    ) -> list[dict[str, Any]]:
        """Получить доступы группы"""

        cache_key = f"group:{group_id}:accesses"
        
        cached = await self._get_from_cache(
            cache_key=cache_key,
            response_key="accesses",
            use_cache=use_cache,
            cache_log_message=f"Кэш для группы {group_id} доступов"
        )
        if cached is not None:
            return cached
        
        data = await self._get_json_data(f"groups/{group_id}/accesses", response_key="accesses")
        
        await self._set_to_cache(
            cache_key=cache_key,
            data=data,
            response_key="accesses",
            ttl=GROUP_ACCESSES_TTL,
            use_cache=use_cache,
            cache_log_message=f"Кэш сохранен для группы {group_id} доступов"
        )
        
        return data
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=2, max=10)
    )
    async def get_groups_by_access(
        self,
        access_id: int,
        use_cache: bool = True
    ) -> list[dict[str, Any]]:
        """Получить группы, содержащие данный доступ"""

        cache_key = f"access:{access_id}:groups"
        
        cached = await self._get_from_cache(
            cache_key=cache_key,
            response_key="groups",
            use_cache=use_cache,
            cache_log_message=f"Кэш для доступа {access_id} групп"
        )
        if cached is not None:
            return cached
        
        data = await self._get_json_data(f"accesses/{access_id}/groups", response_key="groups")
        
        await self._set_to_cache(
            cache_key=cache_key,
            data=data,
            response_key="groups",
            ttl=ACCESS_GROUPS_TTL,
            use_cache=use_cache,
            cache_log_message=f"Кэш сохранен для доступа {access_id} групп"
        )
        
        return data
    
    async def invalidate_conflicts_cache(self):
        """Инвалидировать кэш матрицы конфликтов"""
        await self._invalidate_cache(
            "conflicts_matrix",
            "Кэш инвалидирован для матрицы конфликтов"
        )
    
    async def invalidate_group_cache(self, group_id: int):
        """Инвалидировать кэш группы"""
        await self._invalidate_cache(
            f"group:{group_id}:accesses",
            f"Кэш инвалидирован для группы {group_id}"
        )
    
    async def invalidate_access_cache(self, access_id: int):
        """Инвалидировать кэш доступа"""
        await self._invalidate_cache(
            f"access:{access_id}:groups",
            f"Кэш инвалидирован для доступа {access_id}"
        )

