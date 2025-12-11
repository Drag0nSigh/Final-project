from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from user_service.models.enums import PermissionType, PermissionStatus


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(description="ID пользователя")
    username: str = Field(description="Имя пользователя")


class UserPermission(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(description="ID записи права пользователя")
    user_id: int = Field(description="ID пользователя")
    permission_type: PermissionType = Field(description="Тип права")
    item_id: int = Field(description="ID доступа или группы")
    item_name: str | None = Field(default=None, description="Название доступа или группы")
    status: PermissionStatus = Field(description="Статус права пользователя")
    request_id: str = Field(description="UUID заявки/запроса, породившего право")
    assigned_at: datetime | None = Field(default=None, description="Когда право назначено")


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
    id: int = Field(description="ID права")
    permission_type: PermissionType = Field(description="Тип права")
    item_id: int = Field(description="ID ресурса/группы")
    item_name: str | None = Field(default=None, description="Название ресурса/группы")
    status: str = Field(description="Статус права")
    assigned_at: datetime | None = Field(default=None, description="Когда право назначено")


class GetUserPermissionsResponse(BaseModel):
    user_id: int = Field(description="ID пользователя")
    groups: list[PermissionResponse] = Field(default_factory=list, description="Права по группам")
    accesses: list[PermissionResponse] = Field(default_factory=list, description="Права по доступам")


class ActiveGroup(BaseModel):
    id: int = Field(description="ID группы")
    name: str | None = Field(default=None, description="Название группы")


class GetActiveGroupsResponse(BaseModel):
    groups: list[ActiveGroup] = Field(default_factory=list, description="Список активных групп")


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="Имя пользователя")


class CreateUserResponse(BaseModel):
    id: int = Field(description="ID созданного пользователя")
    username: str = Field(description="Имя созданного пользователя")


class CreateUserPermissionRequest(BaseModel):
    user_id: int = Field(gt=0, description="ID пользователя")
    permission_type: PermissionType = Field(description="Тип права: access или group")
    item_id: int = Field(gt=0, description="ID доступа или группы")
    status: PermissionStatus = Field(default=PermissionStatus.ACTIVE, description="Статус права")
    item_name: str | None = Field(default=None, description="Название доступа или группы")
    request_id: str | None = Field(default=None, description="UUID запроса (опционально, будет сгенерирован если не указан)")


class CreateUserPermissionResponse(BaseModel):
    id: int = Field(description="ID созданного права")
    user_id: int = Field(description="ID пользователя")
    permission_type: str = Field(description="Тип права")
    item_id: int = Field(description="ID доступа или группы")
    item_name: str | None = Field(default=None, description="Название доступа или группы")
    status: str = Field(description="Статус права")
    request_id: str = Field(description="UUID заявки")
    assigned_at: datetime | None = Field(default=None, description="Когда право назначено")


class UpdatePermissionStatusRequest(BaseModel):
    status: PermissionStatus = Field(description="Новый статус: 'active' или 'rejected'")
    reason: str | None = Field(default=None, description="Причина отклонения (опционально)")


class UpdatePermissionStatusResponse(BaseModel):
    request_id: str = Field(description="UUID заявки")
    status: str = Field(description="Итоговый статус заявки")
    message: str = Field(description="Сообщение о результате операции")