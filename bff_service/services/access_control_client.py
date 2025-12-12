import httpx

from bff_service.models.models import Resource, Access, Group, GetConflictsResponse
from bff_service.services.protocols import (
    HTTPClientProtocol,
    ResourceClientProtocol,
    AccessClientProtocol,
    GroupClientProtocol,
    ConflictClientProtocol,
)
from bff_service.services.resource_client import ResourceClient
from bff_service.services.access_client import AccessClient
from bff_service.services.group_client import GroupClient
from bff_service.services.conflict_client import ConflictClient


class AccessControlClient:

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        http_client: HTTPClientProtocol | None = None,
        resource_client: ResourceClientProtocol | None = None,
        access_client: AccessClientProtocol | None = None,
        group_client: GroupClientProtocol | None = None,
        conflict_client: ConflictClientProtocol | None = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: HTTPClientProtocol = (
            http_client
            if http_client is not None
            else httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout)
        )

        self._resources: ResourceClientProtocol = (
            resource_client
            if resource_client is not None
            else ResourceClient(self._base_url, self._client)
        )
        self._accesses: AccessClientProtocol = (
            access_client
            if access_client is not None
            else AccessClient(self._base_url, self._client)
        )
        self._groups: GroupClientProtocol = (
            group_client
            if group_client is not None
            else GroupClient(self._base_url, self._client)
        )
        self._conflicts: ConflictClientProtocol = (
            conflict_client
            if conflict_client is not None
            else ConflictClient(self._base_url, self._client)
        )

    async def get_all_resources(self) -> list[Resource]:
        return await self._resources.get_all()

    async def get_resource(self, resource_id: int) -> Resource:
        return await self._resources.get_by_id(resource_id)

    async def get_all_accesses(self) -> list[Access]:
        return await self._accesses.get_all()

    async def get_access(self, access_id: int) -> Access:
        return await self._accesses.get_by_id(access_id)

    async def get_all_groups(self) -> list[Group]:
        return await self._groups.get_all()

    async def get_group(self, group_id: int) -> Group:
        return await self._groups.get_by_id(group_id)

    async def get_conflicts(self) -> GetConflictsResponse:
        return await self._conflicts.get_all()

    async def close(self):
        await self._client.aclose()
