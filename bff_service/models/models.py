from datetime import datetime
from pydantic import BaseModel, Field

from bff_service.models.enums import PermissionType, PermissionStatus


# Модели для запроса доступа
class RequestAccessRequest(BaseModel):
    """Модель для создания заявки на доступ/группу прав"""
    user_id: int = Field(gt=0, description="ID пользователя")
    permission_type: PermissionType = Field(description="Тип права: access или group")
    item_id: int = Field(gt=0, description="ID доступа или группы")


class RequestAccessResponse(BaseModel):
    """Модель ответа при создании заявки"""
    status: str = Field(default="accepted", description="Статус обработки заявки")
    request_id: str = Field(description="UUID заявки для отслеживания")


# Модели для отзыва прав
class RevokePermissionRequest(BaseModel):
    """Модель для отзыва права"""
    permission_type: PermissionType = Field(description="Тип права")
    item_id: int = Field(gt=0, description="ID доступа или группы")


class RevokePermissionResponse(BaseModel):
    """Модель ответа при отзыве права"""
    status: str = Field(default="revoked", description="Статус отзыва права")


# Модели для получения прав
class PermissionResponse(BaseModel):
    """Модель для отдельного права с деталями"""
    id: int
    permission_type: PermissionType
    item_id: int
    item_name: str | None = None  # Название доступа/группы (опционально)
    status: str
    assigned_at: datetime | None = None


class GetUserPermissionsResponse(BaseModel):
    """Модель для получения всех прав пользователя"""
    user_id: int
    groups: list[PermissionResponse] = Field(default_factory=list)
    accesses: list[PermissionResponse] = Field(default_factory=list)


# Модели для работы с заявками (трекинг)
class UserPermissionResponse(BaseModel):
    """Модель заявки/права пользователя"""
    id: int
    user_id: int
    permission_type: PermissionType
    item_id: int
    status: PermissionStatus
    request_id: str
    assigned_at: datetime | None = None


class Resource(BaseModel):
    """Модель ресурса"""
    id: int
    name: str
    type: str
    description: str | None = None


class Access(BaseModel):
    """Модель доступа"""
    id: int
    name: str
    resources: list[Resource] = Field(default_factory=list)


class Group(BaseModel):
    """Модель группы"""
    id: int
    name: str
    accesses: list[Access] = Field(default_factory=list)


class Conflict(BaseModel):
    """Модель конфликта"""
    group_id1: int
    group_id2: int


class GetConflictsResponse(BaseModel):
    """Модель для получения всех конфликтов"""
    conflicts: list[Conflict] = Field(default_factory=list)

