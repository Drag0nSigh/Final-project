from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Модели для запроса доступа
class RequestAccessIn(BaseModel):
    """Модель для создания заявки на доступ/группу прав"""
    user_id: int = Field(gt=0, description="ID пользователя")
    permission_type: Literal["access", "group"] = Field(description="Тип права: access или group")
    item_id: int = Field(gt=0, description="ID доступа или группы")


class RequestAccessOut(BaseModel):
    """Модель ответа при создании заявки"""
    status: str = Field(default="accepted", description="Статус обработки заявки")
    request_id: str = Field(description="UUID заявки для отслеживания")


# Модели для отзыва прав
class RevokePermissionIn(BaseModel):
    """Модель для отзыва права"""
    permission_type: Literal["access", "group"] = Field(description="Тип права")
    item_id: int = Field(gt=0, description="ID доступа или группы")


class RevokePermissionOut(BaseModel):
    """Модель ответа при отзыве права"""
    status: str = Field(default="revoked", description="Статус отзыва права")


# Модели для получения прав
class PermissionOut(BaseModel):
    """Модель для отдельного права с деталями"""
    id: int
    permission_type: Literal["access", "group"]
    item_id: int
    item_name: Optional[str] = None  # Название доступа/группы (опционально)
    status: str
    assigned_at: Optional[datetime] = None


class GetUserPermissionsOut(BaseModel):
    """Модель для получения всех прав пользователя"""
    user_id: int
    groups: list[PermissionOut] = Field(default_factory=list)
    accesses: list[PermissionOut] = Field(default_factory=list)


# Модели для работы с заявками (трекинг)
class UserPermissionOut(BaseModel):
    """Модель заявки/права пользователя"""
    id: int
    user_id: int
    permission_type: Literal["access", "group"]
    item_id: int
    status: Literal["active", "pending", "revoked", "rejected"]
    request_id: str
    assigned_at: Optional[datetime] = None


class Resource(BaseModel):
    """Модель ресурса"""
    id: int
    name: str
    type: str
    description: Optional[str] = None


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


class GetConflictsOut(BaseModel):
    """Модель для получения всех конфликтов"""
    conflicts: list[Conflict] = Field(default_factory=list)

