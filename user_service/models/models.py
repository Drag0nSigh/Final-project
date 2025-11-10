from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class UserPermission(BaseModel):
    """***ВАЖНО для BFF Service***: Модель права пользователя.
    
    Используется в ответах эндпоинтов. Поле ``status`` может быть: "active", "pending", "revoked", "rejected".
    Поле ``item_name`` содержит название доступа/группы (может быть None, если не заполнено).
    Поле ``request_id`` используется для отслеживания заявки через весь жизненный цикл.
    """
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    permission_type: Literal["access", "group"]
    item_id: int
    item_name: Optional[str] = None
    status: Literal["active", "pending", "revoked"]
    request_id: str  # UUID в виде строки
    assigned_at: Optional[datetime] = None


# Pydantic модели для ввода (Input)
class RequestAccessIn(BaseModel):
    """***ВАЖНО для BFF Service***: Модель запроса на создание заявки.
    
    Используется в эндпоинте POST /request. BFF должен отправлять запросы в этом формате.
    """
    user_id: int = Field(gt=0, description="ID пользователя")
    permission_type: Literal["access", "group"] = Field(description="Тип права: access или group")
    item_id: int = Field(gt=0, description="ID доступа или группы")


class RequestAccessOut(BaseModel):
    """***ВАЖНО для BFF Service***: Модель ответа при создании заявки.
    
    BFF получает этот ответ от User Service и передаёт клиенту. Поле ``request_id``
    используется для отслеживания статуса заявки (клиент может проверить статус через
    GET /users/{user_id}/permissions).
    """
    status: str = Field(default="accepted", description="Статус обработки заявки")
    request_id: str = Field(description="UUID заявки для отслеживания")


class RevokePermissionIn(BaseModel):
    permission_type: Literal["access", "group"] = Field(description="Тип права")
    item_id: int = Field(gt=0, description="ID доступа или группы")


class RevokePermissionOut(BaseModel):
    status: str = Field(default="revoked", description="Статус отзыва права")


class PermissionOut(BaseModel):
    """Модель для отдельного права с деталями.
    
    ***ВАЖНО для BFF Service***: Используется в ``GetUserPermissionsOut`` для представления
    отдельного права (доступа или группы). Поле ``status`` может быть: "active", "pending",
    "revoked", "rejected". Поле ``item_name`` содержит название доступа/группы из Access Control
    Service (может быть None, если не заполнено).
    """
    id: int
    permission_type: Literal["access", "group"]
    item_id: int
    item_name: Optional[str] = None  # Название доступа/группы (опционально)
    status: str
    assigned_at: Optional[datetime] = None


class GetUserPermissionsOut(BaseModel):
    """Модель для получения всех прав пользователя.
    
    ***ВАЖНО для BFF Service***: BFF использует этот формат ответа для отображения прав
    пользователя клиенту. Поля ``groups`` и ``accesses`` содержат списки прав, разделённые
    по типу. Каждый элемент содержит полную информацию о праве (id, type, item_id, item_name,
    status, assigned_at).
    """
    user_id: int
    groups: list[PermissionOut] = Field(default_factory=list)
    accesses: list[PermissionOut] = Field(default_factory=list)


class ActiveGroup(BaseModel):
    """Модель одной активной группы"""
    id: int
    name: Optional[str] = None


class GetActiveGroupsOut(BaseModel):
    """Модель для получения активных групп (для Validation Service) - список групп.
    
    ***ВАЖНО для Validation Service***: Validation Service использует этот формат для получения
    активных групп пользователя при проверке конфликтов. Формат: ``{"groups": [{"id": int, "name": str}, ...]}``.
    Возвращаются только группы со статусом ``active``.
    """
    groups: list[ActiveGroup] = Field(default_factory=list)


# Служебные модели для создания объектов
class CreateUserIn(BaseModel):
    """Модель для создания пользователя (служебный эндпоинт)"""
    username: str = Field(..., min_length=1, max_length=50, description="Имя пользователя")


class CreateUserOut(BaseModel):
    """Модель ответа при создании пользователя"""
    id: int
    username: str


class CreateUserPermissionIn(BaseModel):
    """Модель для создания UserPermission (служебный эндпоинт)"""
    user_id: int = Field(gt=0, description="ID пользователя")
    permission_type: Literal["access", "group"] = Field(description="Тип права: access или group")
    item_id: int = Field(gt=0, description="ID доступа или группы")
    status: Literal["active", "pending", "revoked"] = Field(default="active", description="Статус права")
    item_name: Optional[str] = Field(default=None, description="Название доступа или группы")
    request_id: Optional[str] = Field(default=None, description="UUID запроса (опционально, будет сгенерирован если не указан)")


class CreateUserPermissionOut(BaseModel):
    """Модель ответа при создании UserPermission"""
    id: int
    user_id: int
    permission_type: str
    item_id: int
    item_name: Optional[str] = None
    status: str
    request_id: str
    assigned_at: Optional[datetime] = None


class UpdatePermissionStatusIn(BaseModel):
    """Модель для обновления статуса заявки (активация/отклонение)"""
    status: Literal["active", "rejected"] = Field(description="Новый статус: 'active' или 'rejected'")
    reason: Optional[str] = Field(default=None, description="Причина отклонения (опционально)")


class UpdatePermissionStatusOut(BaseModel):
    """Модель ответа при обновлении статуса заявки"""
    request_id: str
    status: str
    message: str = Field(description="Сообщение о результате операции")