from bff_service.models.models import Group
from bff_service.services.base_http_client import BaseHTTPClient
from bff_service.services.protocols import HTTPClientProtocol


class GroupClient(BaseHTTPClient[Group]):

    def __init__(
        self,
        base_url: str,
        http_client: HTTPClientProtocol,
    ):
        super().__init__(base_url, "groups", http_client)

    async def get_all(self) -> list[Group]:
        return await self._get_list(Group)

    async def get_by_id(self, group_id: int) -> Group:
        return await self._get_one(group_id, Group)
