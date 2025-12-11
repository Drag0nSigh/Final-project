from bff_service.models.models import Access
from bff_service.services.base_http_client import BaseHTTPClient
from bff_service.services.protocols import HTTPClientProtocol


class AccessClient(BaseHTTPClient[Access]):

    def __init__(
        self,
        base_url: str,
        http_client: HTTPClientProtocol,
    ):
        super().__init__(base_url, "accesses", http_client)

    async def get_all(self) -> list[Access]:
        return await self._get_list(Access)

    async def get_by_id(self, access_id: int) -> Access:
        return await self._get_one(access_id, Access)
