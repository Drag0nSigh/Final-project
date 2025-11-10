import logging
import httpx
from typing import Any

logger = logging.getLogger(__name__)


class UserServiceClient:
    """HTTP клиент для взаимодействия с User Service."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)

    async def request_access(
        self, user_id: int, permission_type: str, item_id: int
    ) -> dict[str, Any]:
        """Создание заявки на получение доступа или группы прав."""

        url = "/request"
        payload = {
            "user_id": user_id,
            "permission_type": permission_type,
            "item_id": item_id,
        }

        logger.debug(f"Отправка запроса в User Service: POST {url} с данными {payload}")

        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от User Service: {result}")
        return result

    async def revoke_permission(
        self, user_id: int, permission_type: str, item_id: int
    ) -> dict[str, Any]:
        """Отзыв права у пользователя."""

        url = f"/users/{user_id}/permissions"
        payload = {
            "permission_type": permission_type,
            "item_id": item_id,
        }

        logger.debug(f"Отправка запроса в User Service: DELETE {url} с данными {payload}")

        response = await self.client.request("DELETE", url, json=payload)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от User Service: {result}")
        return result

    async def get_user_permissions(self, user_id: int) -> dict[str, Any]:
        """Получение всех прав пользователя."""
        
        url = f"/users/{user_id}/permissions"

        logger.debug(f"Отправка запроса в User Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от User Service: {result}")
        return result

    async def close(self):
        """Закрыть HTTP клиент."""
        await self.client.aclose()

