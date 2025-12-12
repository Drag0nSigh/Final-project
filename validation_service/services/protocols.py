from typing import Protocol

from validation_service.models.validation_models import (
    ValidationRequest,
    ValidationResult
)
from validation_service.models.service_models import (
    GetConflictsResponse,
    GetGroupAccessesResponse,
    GetAccessGroupsResponse,
    GetUserGroupsResponse,
)


class UserServiceClientProtocol(Protocol):

    async def get_user_active_groups(
        self,
        user_id: int,
        use_cache: bool = True
    ) -> GetUserGroupsResponse:
        ...

    async def invalidate_user_cache(self, user_id: int) -> None:
        ...

    async def close(self) -> None:
        ...


class AccessControlClientProtocol(Protocol):

    async def get_conflicts_matrix(
        self,
        use_cache: bool = True
    ) -> GetConflictsResponse:
        ...

    async def get_group_accesses(
        self,
        group_id: int,
        use_cache: bool = True
    ) -> GetGroupAccessesResponse:
        ...

    async def get_groups_by_access(
        self,
        access_id: int,
        use_cache: bool = True
    ) -> GetAccessGroupsResponse:
        ...

    async def invalidate_conflicts_cache(self) -> None:
        ...

    async def invalidate_group_cache(self, group_id: int) -> None:
        ...

    async def invalidate_access_cache(self, access_id: int) -> None:
        ...

    async def close(self) -> None:
        ...


class ValidationServiceProtocol(Protocol):

    async def validate(self, request: ValidationRequest) -> ValidationResult:
        ...
