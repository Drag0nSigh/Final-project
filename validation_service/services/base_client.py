"""
Базовый класс для HTTP клиентов с поддержкой кэширования

Содержит общую логику кэширования для всех клиентов.
"""

import logging
from typing import Any, Optional, Callable, Awaitable
import httpx

from validation_service.services.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class BaseServiceClient:
    """Базовый класс для HTTP клиентов с кэшированием"""
    
    def __init__(
        self,
        base_url: str,
        cache: Optional[RedisCache] = None,
        timeout: float = 30.0
    ):
        """Инициализация базового клиента"""
        
        self.base_url = base_url.rstrip('/')
        self.cache = cache
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Закрыть HTTP клиент"""

        await self.client.aclose()
    
    async def _cached_request(
        self,
        cache_key: str,
        fetch_func: Callable[[], Awaitable[Any]],
        ttl: int,
        response_key: Optional[str] = None,
        use_cache: bool = True,
        cache_log_message: Optional[str] = None
    ) -> Any:
        """Универсальный метод для запроса с кэшированием"""

        # Проверка кэша
        if use_cache and self.cache:
            cached = await self.cache.get_json(cache_key)
            if cached is not None:
                log_msg = cache_log_message or f"Кэш hit для {cache_key}"
                logger.debug(log_msg)
                
                # Если указан response_key, извлекаем значение по ключу
                if response_key:
                    return cached.get(response_key, [])
                return cached
        
        data = await fetch_func()
        
        # Сохранение в кэш
        if use_cache and self.cache:
            if response_key:
                cache_value = {response_key: data}
            else:
                cache_value = data
            
            await self.cache.setex_json(
                cache_key,
                ttl=ttl,
                value=cache_value
            )
            
            log_msg = cache_log_message or f"Кэш сохранен для {cache_key}"
            logger.debug(log_msg)
        
        return data

