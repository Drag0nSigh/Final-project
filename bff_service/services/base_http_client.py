from typing import TypeVar, Generic

from bff_service.services.protocols import HTTPClientProtocol

T = TypeVar("T")


class BaseHTTPClient(Generic[T]):

    def __init__(
        self,
        base_url: str,
        endpoint_prefix: str,
        http_client: HTTPClientProtocol,
    ):
        self.base_url = base_url.rstrip("/")
        self.endpoint_prefix = endpoint_prefix
        self.client = http_client

    async def _get_list(self, model_class: type[T]) -> list[T]:
        url = f"/{self.endpoint_prefix}"

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        return [model_class.model_validate(item) for item in result]

    async def _get_one(self, entity_id: int, model_class: type[T]) -> T:
        url = f"/{self.endpoint_prefix}/{entity_id}"

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        return model_class.model_validate(result)

