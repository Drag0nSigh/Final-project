import json
import logging
from typing import Any

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class RedisCache:
    
    def __init__(self, redis_host: str = "redis", redis_port: int = 6379):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.client: redis.Redis | None = None
    
    async def connect(self):
        try:
            self.client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True
            )
            await self.client.ping()
            logger.info(f"Подключение к Redis успешно: {self.redis_host}:{self.redis_port}")
        except Exception as e:
            logger.error(f"Неудачное подключение к Redis: {e}")
            raise
    
    async def close(self):
        if self.client:
            await self.client.close()
            logger.info("Подключение к Redis закрыто")
    
    async def get(self, key: str) -> str | None:

        if not self.client:
            return None
        
        try:
            value = await self.client.get(key)
            return value
        except Exception as e:
            logger.error(f"Ошибка при получении значения из кэша {key}: {e}")
            return None
    
    async def setex(self, key: str, ttl: int, value: str) -> None:

        if not self.client:
            return
        
        try:
            await self.client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Ошибка при установке значения в кэш {key}: {e}")
    
    async def delete(self, key: str) -> None:

        if not self.client:
            return
        
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
    
    async def get_json(self, key: str) -> Any | None:

        value = await self.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка при парсинге JSON из кэша {key}: {e}")
            return None
    
    async def setex_json(self, key: str, ttl: int, value: Any) -> None:

        try:
            json_value = json.dumps(value)
            await self.setex(key, ttl, json_value)
        except (TypeError, ValueError) as e:
            logger.error(f"Ошибка при сериализации JSON для кэша {key}: {e}")

