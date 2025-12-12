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
    id: int = Field(description="ID записи права")
    permission_type: PermissionType = Field(description="Тип права: access или group")
    item_id: int = Field(description="ID ресурса или группы, к которому относится право")
    item_name: str | None = Field(default=None, description="Имя ресурса/группы, если доступно")
    status: str = Field(description="Текущий статус права")
    assigned_at: datetime | None = Field(default=None, description="Дата и время назначения права")


class GetUserPermissionsResponse(BaseModel):
    user_id: int = Field(description="ID пользователя")
    groups: list[PermissionResponse] = Field(default_factory=list, description="Список прав по группам")
    accesses: list[PermissionResponse] = Field(default_factory=list, description="Список прав по доступам")


class UserPermissionResponse(BaseModel):
    id: int = Field(description="ID права пользователя")
    user_id: int = Field(description="ID пользователя")
    permission_type: PermissionType = Field(description="Тип права")
    item_id: int = Field(description="ID доступа или группы")
    status: PermissionStatus = Field(description="Статус права пользователя")
    request_id: str = Field(description="ID заявки, из которой появилось право")
    assigned_at: datetime | None = Field(default=None, description="Когда право назначено")


class Resource(BaseModel):
    id: int = Field(description="ID ресурса")
    name: str = Field(description="Название ресурса")
    type: str = Field(description="Тип ресурса")
    description: str | None = Field(default=None, description="Описание ресурса")


class Access(BaseModel):
    id: int = Field(description="ID доступа")
    name: str = Field(description="Название доступа")
    resources: list[Resource] = Field(default_factory=list, description="Ресурсы, связанные с доступом")


class Group(BaseModel):
    id: int = Field(description="ID группы")
    name: str = Field(description="Название группы")
    accesses: list[Access] = Field(default_factory=list, description="Доступы, входящие в группу")


class Conflict(BaseModel):
    group_id1: int = Field(description="ID первой конфликтующей группы")
    group_id2: int = Field(description="ID второй конфликтующей группы")


class GetConflictsResponse(BaseModel):
    conflicts: list[Conflict] = Field(default_factory=list, description="Список конфликтующих групп")
