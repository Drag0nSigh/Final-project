from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.db.resource import Resource
from access_control_service.db.access import Access
from access_control_service.db.group import Group
from access_control_service.models.models import (
    CreateResourceRequest,
    CreateResourceResponse,
    CreateAccessRequest,
    CreateAccessResponse,
    CreateGroupRequest,
    CreateGroupResponse,
    GetGroupAccessesResponse,
    GetAccessGroupsResponse,
    CreateConflictRequest,
    CreateConflictResponse,
    Conflict as ConflictModel,
)


class ResourceServiceProtocol(Protocol):

    async def get_resource(self, resource_id: int) -> Resource:
        ...

    async def get_all_resources(self) -> list[Resource]:
        ...


class ResourceServiceAdminProtocol(Protocol):

    async def create_resource(
        self, resource_data: CreateResourceRequest
    ) -> CreateResourceResponse:
        ...

    async def delete_resource(self, resource_id: int) -> None:
        ...


class AccessServiceProtocol(Protocol):

    async def create_access(
        self, access_data: CreateAccessRequest
    ) -> CreateAccessResponse:
        ...

    async def get_access(self, access_id: int) -> Access:
        ...

    async def get_all_accesses(self) -> list[Access]:
        ...

    async def get_groups_containing_access(
        self, access_id: int
    ) -> GetAccessGroupsResponse:
        ...


class AccessServiceAdminProtocol(Protocol):

    async def add_resource_to_access(
        self, access_id: int, resource_id: int
    ) -> None:
        ...

    async def remove_resource_from_access(
        self, access_id: int, resource_id: int
    ) -> None:
        ...

    async def delete_access(self, access_id: int) -> None:
        ...


class GroupServiceProtocol(Protocol):

    async def create_group(
        self, group_data: CreateGroupRequest
    ) -> CreateGroupResponse:
        ...

    async def get_group(self, group_id: int) -> Group:
        ...

    async def get_all_groups(self) -> list[Group]:
        ...

    async def get_group_accesses(
        self, group_id: int
    ) -> GetGroupAccessesResponse:
        ...

    async def add_access_to_group(
        self, group_id: int, access_id: int
    ) -> None:
        ...

    async def remove_access_from_group(
        self, group_id: int, access_id: int
    ) -> None:
        ...

    async def delete_group(self, group_id: int) -> None:
        ...


class ConflictServiceProtocol(Protocol):

    async def get_all_conflicts(self) -> list[ConflictModel]:
        ...


class ConflictServiceAdminProtocol(Protocol):

    async def create_conflict(
        self, conflict_data: CreateConflictRequest
    ) -> list[CreateConflictResponse]:
        ...

    async def delete_conflict(
        self, group_id1: int, group_id2: int
    ) -> None:
        ...

