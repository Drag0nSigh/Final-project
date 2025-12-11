from bff_service.models.models import GetConflictsResponse
from bff_service.services.base_http_client import BaseHTTPClient
from bff_service.services.protocols import HTTPClientProtocol


class ConflictClient(BaseHTTPClient[GetConflictsResponse]):

    def __init__(
        self,
        base_url: str,
        http_client: HTTPClientProtocol,
    ):
        super().__init__(base_url, "conflicts", http_client)

    async def get_all(self) -> GetConflictsResponse:
        url = f"/{self.endpoint_prefix}"

        response = await self.client.get(url)
        response.raise_for_status()
        result = response.json()
        return GetConflictsResponse.model_validate(result)
