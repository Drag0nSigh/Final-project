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
    """Модель запроса на создание заявки."""

    user_id: int = Field(gt=0, description="ID пользователя")
    permission_type: PermissionType = Field(description="Тип права: access или group")
    item_id: int = Field(gt=0, description="ID доступа или группы")


class RequestAccessResponse(BaseModel):
    """Модель ответа при создании заявки."""

    status: str = Field(default="accepted", description="Статус обработки заявки")
    request_id: str = Field(description="UUID заявки для отслеживания")


class RevokePermissionRequest(BaseModel):
    """Модель запроса на отзыв права у пользователя."""

    permission_type: PermissionType = Field(description="Тип права")
    item_id: int = Field(gt=0, description="ID доступа или группы")


class RevokePermissionResponse(BaseModel):
    """Модель ответа при отзыве права у пользователя."""

    status: str = Field(default="revoked", description="Статус отзыва права")


class PermissionResponse(BaseModel):
    """Модель для отдельного права с деталями."""

    id: int
    permission_type: PermissionType
    item_id: int
    item_name: str | None = None  # Название доступа/группы (опционально)
    status: str
    assigned_at: datetime | None = None


class GetUserPermissionsResponse(BaseModel):
    """Модель для получения всех прав пользователя."""

    user_id: int
    groups: list[PermissionResponse] = Field(default_factory=list)
    accesses: list[PermissionResponse] = Field(default_factory=list)


class ActiveGroup(BaseModel):
    """Модель одной активной группы"""
    id: int
    name: str | None = None


class GetActiveGroupsResponse(BaseModel):
    """Модель для получения активных групп (для Validation Service) - список групп."""
    
    groups: list[ActiveGroup] = Field(default_factory=list)


class CreateUserRequest(BaseModel):
    """Модель для создания пользователя (служебный эндпоинт)"""
    username: str = Field(..., min_length=1, max_length=50, description="Имя пользователя")


class CreateUserResponse(BaseModel):
    """Модель ответа при создании пользователя"""
    id: int
    username: str


class CreateUserPermissionRequest(BaseModel):
    """Модель для создания UserPermission (служебный эндпоинт)"""
    user_id: int = Field(gt=0, description="ID пользователя")
    permission_type: PermissionType = Field(description="Тип права: access или group")
    item_id: int = Field(gt=0, description="ID доступа или группы")
    status: PermissionStatus = Field(default=PermissionStatus.ACTIVE, description="Статус права")
    item_name: str | None = Field(default=None, description="Название доступа или группы")
    request_id: str | None = Field(default=None, description="UUID запроса (опционально, будет сгенерирован если не указан)")


class CreateUserPermissionResponse(BaseModel):
    """Модель ответа при создании UserPermission"""
    id: int
    user_id: int
    permission_type: str
    item_id: int
    item_name: str | None = None
    status: str
    request_id: str
    assigned_at: datetime | None = None


class UpdatePermissionStatusRequest(BaseModel):
    """Модель для обновления статуса заявки (активация/отклонение)"""
    status: PermissionStatus = Field(description="Новый статус: 'active' или 'rejected'")
    reason: str | None = Field(default=None, description="Причина отклонения (опционально)")


class UpdatePermissionStatusResponse(BaseModel):
    """Модель ответа при обновлении статуса заявки"""
    request_id: str
    status: str
    message: str = Field(description="Сообщение о результате операции")