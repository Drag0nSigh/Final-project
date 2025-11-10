import logging
import httpx
from typing import Any

logger = logging.getLogger(__name__)


class AccessControlClient:
    """HTTP клиент для взаимодействия с Access Control Service."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        """Инициализация клиента."""
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def get_all_resources(self) -> list[dict[str, Any]]:
        """Получение всех ресурсов."""
        url = "/resources"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: {len(result)} ресурсов")
        return result

    async def get_resource(self, resource_id: int) -> dict[str, Any]:
        """Получение ресурса по ID."""
        url = f"/resources/{resource_id}"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: ресурс {resource_id}")
        return result

    async def get_all_accesses(self) -> list[dict[str, Any]]:
        """Получение всех доступов."""
        url = "/accesses"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: {len(result)} доступов")
        return result

    async def get_access(self, access_id: int) -> dict[str, Any]:
        """Получение доступа по ID."""
        url = f"/accesses/{access_id}"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: доступ {access_id}")
        return result

    async def get_all_groups(self) -> list[dict[str, Any]]:
        """Получение всех групп."""
        url = "/groups"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: {len(result)} групп")
        return result

    async def get_group(self, group_id: int) -> dict[str, Any]:
        """Получение группы по ID."""
        url = f"/groups/{group_id}"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: группа {group_id}")
        return result

    async def get_conflicts(self) -> dict[str, Any]:
        """Получение всех конфликтов."""
        url = "/conflicts"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: {len(result.get('conflicts', []))} конфликтов")
        return result

    async def close(self):
        """Закрыть HTTP клиент."""
        await self.client.aclose()
