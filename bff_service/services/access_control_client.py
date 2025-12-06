import logging
import httpx

from bff_service.models.models import Resource, Access, Group, GetConflictsResponse

logger = logging.getLogger(__name__)


class AccessControlClient:
    """HTTP клиент для взаимодействия с Access Control Service."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        """Инициализация клиента."""
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def get_all_resources(self) -> list[Resource]:
        """Получение всех ресурсов."""
        url = "/resources"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: {len(result)} ресурсов")
        return [Resource.model_validate(item) for item in result]

    async def get_resource(self, resource_id: int) -> Resource:
        """Получение ресурса по ID."""
        url = f"/resources/{resource_id}"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: ресурс {resource_id}")
        return Resource.model_validate(result)

    async def get_all_accesses(self) -> list[Access]:
        """Получение всех доступов."""
        url = "/accesses"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: {len(result)} доступов")
        return [Access.model_validate(item) for item in result]

    async def get_access(self, access_id: int) -> Access:
        """Получение доступа по ID."""
        url = f"/accesses/{access_id}"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: доступ {access_id}")
        return Access.model_validate(result)

    async def get_all_groups(self) -> list[Group]:
        """Получение всех групп."""
        url = "/groups"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: {len(result)} групп")
        return [Group.model_validate(item) for item in result]

    async def get_group(self, group_id: int) -> Group:
        """Получение группы по ID."""
        url = f"/groups/{group_id}"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: группа {group_id}")
        return Group.model_validate(result)

    async def get_conflicts(self) -> GetConflictsResponse:
        """Получение всех конфликтов."""
        url = "/conflicts"

        logger.debug(f"Отправка запроса в Access Control Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от Access Control Service: {len(result.get('conflicts', []))} конфликтов")
        return GetConflictsResponse.model_validate(result)

    async def close(self):
        """Закрыть HTTP клиент."""
        await self.client.aclose()
