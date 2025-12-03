"""
Базовый класс для HTTP клиентов с поддержкой кэширования

Содержит общую логику кэширования для всех клиентов.
"""

import logging
from typing import Any, Callable, Awaitable
import httpx

from validation_service.services.redis_cache import RedisCache

logger = logging.getLogger(__name__)


class BaseServiceClient:
    """Базовый класс для HTTP клиентов с кэшированием"""
    
    def __init__(
        self,
        base_url: str,
        cache: RedisCache | None = None,
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
    
    async def _get_from_cache(
        self,
        cache_key: str,
        response_key: str | None = None,
        use_cache: bool = True,
        cache_log_message: str | None = None
    ) -> Any | None:
        """Получить данные из кэша"""
        
        if use_cache and self.cache:
            cached = await self.cache.get_json(cache_key)
            if cached is not None:
                log_msg = cache_log_message or f"Кэш hit для {cache_key}"
                logger.debug(log_msg)
                
                if response_key:
                    return cached.get(response_key, [])
                return cached
        
        return None
    
    async def _set_to_cache(
        self,
        cache_key: str,
        data: Any,
        response_key: str | None = None,
        ttl: int = 3600,
        use_cache: bool = True,
        cache_log_message: str | None = None
    ) -> None:
        """Сохранить данные в кэш"""
        
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
    
    async def _invalidate_cache(
        self,
        cache_key: str,
        log_message: str | None = None
    ) -> None:
        """Инвалидировать кэш по ключу"""
        
        if self.cache:
            await self.cache.delete(cache_key)
            log_msg = log_message or f"Кэш инвалидирован для {cache_key}"
            logger.debug(log_msg)
    
    async def _get_json_data(
        self,
        path: str,
        response_key: str | None = None,
        default: Any = []
    ) -> Any:
        """Выполнить GET запрос и извлечь данные из JSON ответа"""
        
        url = f"{self.base_url}/{path.lstrip('/')}"
        response = await self.client.get(url)
        response.raise_for_status()
        
        data = response.json()
        if response_key:
            return data.get(response_key, default)
        return data
    
    async def _cached_request(
        self,
        cache_key: str,
        fetch_func: Callable[[], Awaitable[Any]],
        ttl: int,
        response_key: str | None = None,
        use_cache: bool = True,
        cache_log_message: str | None = None
    ) -> Any:
        """Универсальный метод для запроса с кэшированием"""

        if use_cache and self.cache:
            cached = await self.cache.get_json(cache_key)
            if cached is not None:
                log_msg = cache_log_message or f"Кэш hit для {cache_key}"
                logger.debug(log_msg)
                
                if response_key:
                    return cached.get(response_key, [])
                return cached
        
        data = await fetch_func()
        
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

