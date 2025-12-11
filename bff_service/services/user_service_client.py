import logging
import httpx

from bff_service.models.models import RequestAccessResponse, RevokePermissionResponse, GetUserPermissionsResponse
from bff_service.services.protocols import HTTPClientProtocol

logger = logging.getLogger(__name__)


class UserServiceClient:

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        http_client: HTTPClientProtocol | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.client: HTTPClientProtocol = (
            http_client
            if http_client is not None
            else httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        )

    async def request_access(
        self, user_id: int, permission_type: str, item_id: int
    ) -> RequestAccessResponse:

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
        return RequestAccessResponse.model_validate(result)

    async def revoke_permission(
        self, user_id: int, permission_type: str, item_id: int
    ) -> RevokePermissionResponse:

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
        return RevokePermissionResponse.model_validate(result)

    async def get_user_permissions(self, user_id: int) -> GetUserPermissionsResponse:

        url = f"/users/{user_id}/permissions"

        logger.debug(f"Отправка запроса в User Service: GET {url}")

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        logger.debug(f"Получен ответ от User Service: {result}")
        return GetUserPermissionsResponse.model_validate(result)

    async def close(self):
        await self.client.aclose()
