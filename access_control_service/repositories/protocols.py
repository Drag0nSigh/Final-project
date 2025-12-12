from typing import Protocol

from access_control_service.db.access import Access
from access_control_service.db.resource import Resource
from access_control_service.db.group import Group
from access_control_service.db.conflict import Conflict


class AccessRepositoryProtocol(Protocol):

    async def find_by_id_with_resources(self, access_id: int) -> Access | None:
        ...

    async def find_by_id_with_groups(self, access_id: int) -> Access | None:
        ...

    async def find_all_with_resources(self) -> list[Access]:
        ...

    async def find_ids_by_ids(self, access_ids: list[int]) -> set[int]:
        ...

    async def find_by_ids(self, access_ids: list[int]) -> list[Access]:
        ...

    async def find_by_id(self, access_id: int) -> Access | None:
        ...

    async def save(self, access: Access) -> Access:
        ...

    async def flush(self) -> None:
        ...

    async def delete(self, access: Access) -> None:
        ...


class ResourceRepositoryProtocol(Protocol):

    async def find_ids_by_ids(self, resource_ids: list[int]) -> set[int]:
        ...

    async def find_by_ids(self, resource_ids: list[int]) -> list[Resource]:
        ...

    async def find_by_id(self, resource_id: int) -> Resource | None:
        ...

    async def find_by_id_with_accesses(self, resource_id: int) -> Resource | None:
        ...

    async def find_all(self) -> list[Resource]:
        ...

    async def save(self, resource: Resource) -> Resource:
        ...

    async def delete(self, resource: Resource) -> None:
        ...

    async def flush(self) -> None:
        ...


class GroupRepositoryProtocol(Protocol):

    async def find_ids_by_ids(self, group_ids: list[int]) -> set[int]:
        ...

    async def find_by_id_with_accesses_and_resources(self, group_id: int) -> Group | None:
        ...

    async def find_all_with_accesses_and_resources(self) -> list[Group]:
        ...

    async def find_by_id_with_accesses(self, group_id: int) -> Group | None:
        ...

    async def find_by_id_with_conflicts(self, group_id: int) -> Group | None:
        ...

    async def save(self, group: Group) -> Group:
        ...

    async def flush(self) -> None:
        ...

    async def delete(self, group: Group) -> None:
        ...


class ConflictRepositoryProtocol(Protocol):

    async def find_by_group_ids(
        self, group_id1: int, group_id2: int
    ) -> Conflict | None:
        ...

    async def find_all(self) -> list[Conflict]:
        ...

    async def save(self, conflict: Conflict) -> Conflict:
        ...

    async def delete(self, conflict: Conflict) -> None:
        ...

    async def flush(self) -> None:
        ...
