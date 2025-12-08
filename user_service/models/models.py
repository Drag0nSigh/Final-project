from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from user_service.models.enums import PermissionType, PermissionStatus


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class UserPermission(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    permission_type: PermissionType
    item_id: int
    item_name: str | None = None
    status: PermissionStatus
    request_id: str 
    assigned_at: datetime | None = None


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


class ActiveGroup(BaseModel):
    id: int
    name: str | None = None


class GetActiveGroupsResponse(BaseModel):
    
    groups: list[ActiveGroup] = Field(default_factory=list)


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="Имя пользователя")


class CreateUserResponse(BaseModel):
    id: int
    username: str


class CreateUserPermissionRequest(BaseModel):
    user_id: int = Field(gt=0, description="ID пользователя")
    permission_type: PermissionType = Field(description="Тип права: access или group")
    item_id: int = Field(gt=0, description="ID доступа или группы")
    status: PermissionStatus = Field(default=PermissionStatus.ACTIVE, description="Статус права")
    item_name: str | None = Field(default=None, description="Название доступа или группы")
    request_id: str | None = Field(default=None, description="UUID запроса (опционально, будет сгенерирован если не указан)")


class CreateUserPermissionResponse(BaseModel):
    id: int
    user_id: int
    permission_type: str
    item_id: int
    item_name: str | None = None
    status: str
    request_id: str
    assigned_at: datetime | None = None


class UpdatePermissionStatusRequest(BaseModel):
    status: PermissionStatus = Field(description="Новый статус: 'active' или 'rejected'")
    reason: str | None = Field(default=None, description="Причина отклонения (опционально)")


class UpdatePermissionStatusResponse(BaseModel):
    request_id: str
    status: str
    message: str = Field(description="Сообщение о результате операции")