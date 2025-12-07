from bff_service.models.models import Resource
from bff_service.services.base_http_client import BaseHTTPClient
from bff_service.services.protocols import HTTPClientProtocol


class ResourceClient(BaseHTTPClient[Resource]):

    def __init__(
        self,
        base_url: str,
        http_client: HTTPClientProtocol,
    ):
        super().__init__(base_url, "resources", http_client)

    async def get_all(self) -> list[Resource]:
        return await self._get_list(Resource)

    async def get_by_id(self, resource_id: int) -> Resource:
        return await self._get_one(resource_id, Resource)

