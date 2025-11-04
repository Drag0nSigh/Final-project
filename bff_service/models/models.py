from typing import Literal, Optional, List
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
    groups: List[PermissionOut] = Field(default_factory=list)
    accesses: List[PermissionOut] = Field(default_factory=list)


# Модели для получения необходимых доступов для ресурса
class AccessOut(BaseModel):
    """Модель доступа для ресурса"""
    id: int
    name: str
    resources: List[dict] = Field(default_factory=list)  # Упрощенная модель ресурсов


class GetRequiredAccessOut(BaseModel):
    """Модель для получения необходимых доступов для ресурса"""
    resource_id: int
    accesses: List[AccessOut] = Field(default_factory=list)


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

