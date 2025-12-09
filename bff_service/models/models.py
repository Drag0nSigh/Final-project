from datetime import datetime
from pydantic import BaseModel, Field

from bff_service.models.enums import PermissionType, PermissionStatus


class RequestAccessRequest(BaseModel):
    user_id: int = Field(gt=0, description="ID пользователя")
    permission_type: PermissionType = Field(description="Тип права: access или group")
    item_id: int = Field(gt=0, description="ID доступа или группы")


class RequestAccessResponse(BaseModel):
    status: str = Field(default="accepted", description="Статус обработки заявки")
    request_id: str = Field(description="UUID заявки для отслеживания")


class RevokePermissionRequest(BaseModel):
    permission_type: PermissionType = Field(description="Тип права")
    item_id: int = Field(gt=0, description="ID доступа или группы")


class RevokePermissionResponse(BaseModel):
    status: str = Field(default="revoked", description="Статус отзыва права")


class PermissionResponse(BaseModel):
    id: int
    permission_type: PermissionType
    item_id: int
    item_name: str | None = None
    status: str
    assigned_at: datetime | None = None


class GetUserPermissionsResponse(BaseModel):
    user_id: int
    groups: list[PermissionResponse] = Field(default_factory=list)
    accesses: list[PermissionResponse] = Field(default_factory=list)


class UserPermissionResponse(BaseModel):
    id: int
    user_id: int
    permission_type: PermissionType
    item_id: int
    status: PermissionStatus
    request_id: str
    assigned_at: datetime | None = None


class Resource(BaseModel):
    id: int
    name: str
    type: str
    description: str | None = None


class Access(BaseModel):
    id: int
    name: str
    resources: list[Resource] = Field(default_factory=list)


class Group(BaseModel):
    id: int
    name: str
    accesses: list[Access] = Field(default_factory=list)


class Conflict(BaseModel):
    group_id1: int
    group_id2: int


class GetConflictsResponse(BaseModel):
    conflicts: list[Conflict] = Field(default_factory=list)

