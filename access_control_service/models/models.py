from pydantic import BaseModel, ConfigDict, Field

from access_control_service.models.enums import ResourceType


# Pydantic модели для ответов (Output)
class Resource(BaseModel):
    """Модель ресурса"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    type: str
    description: str | None = None


class Access(BaseModel):
    """Модель доступа"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    resources: list[Resource] = Field(default_factory=list)


class Group(BaseModel):
    """Модель группы"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    accesses: list[Access] = Field(default_factory=list)


class Conflict(BaseModel):
    """Модель конфликта"""
    model_config = ConfigDict(from_attributes=True)
    group_id1: int
    group_id2: int


# Pydantic модели для ввода (Input) - служебные эндпоинты
class CreateResourceRequest(BaseModel):
    """Модель для создания ресурса"""
    name: str = Field(..., min_length=1, max_length=100, description="Название ресурса")
    type: ResourceType = Field(..., description="Тип ресурса")
    description: str | None = Field(None, description="Описание ресурса")


class CreateResourceResponse(BaseModel):
    """Модель ответа при создании ресурса"""
    id: int
    name: str
    type: str
    description: str | None = None


class CreateAccessRequest(BaseModel):
    """Модель для создания доступа"""
    name: str = Field(..., min_length=1, max_length=100, description="Название доступа")
    resource_ids: list[int] = Field(default_factory=list, description="Список ID ресурсов")


class CreateAccessResponse(BaseModel):
    """Модель ответа при создании доступа"""
    id: int
    name: str
    resources: list[Resource] = Field(default_factory=list)


class CreateGroupRequest(BaseModel):
    """Модель для создания группы прав"""
    name: str = Field(..., min_length=1, max_length=100, description="Название группы")
    access_ids: list[int] = Field(default_factory=list, description="Список ID доступов")


class CreateGroupResponse(BaseModel):
    """Модель ответа при создании группы"""
    id: int
    name: str
    accesses: list[Access] = Field(default_factory=list)


class CreateConflictRequest(BaseModel):
    """Модель для создания конфликта между группами"""
    group_id1: int = Field(gt=0, description="ID первой группы")
    group_id2: int = Field(gt=0, description="ID второй группы")


class CreateConflictResponse(BaseModel):
    """Модель ответа при создании конфликта"""
    group_id1: int
    group_id2: int


class DeleteConflictRequest(BaseModel):
    """Модель для удаления конфликта между группами"""
    group_id1: int = Field(gt=0, description="ID первой группы")
    group_id2: int = Field(gt=0, description="ID второй группы")


# Модели для API эндпоинтов

class GetGroupAccessesResponse(BaseModel):
    """Модель для получения доступов группы"""
    group_id: int
    accesses: list[Access] = Field(default_factory=list)


class GetAccessGroupsResponse(BaseModel):
    """Модель для получения групп, содержащих доступ"""
    access_id: int
    groups: list[Group] = Field(default_factory=list)


class GetConflictsResponse(BaseModel):
    """Модель для получения всех конфликтов"""
    conflicts: list[Conflict] = Field(default_factory=list)


class AddResourceToAccessRequest(BaseModel):
    """Модель для добавления ресурса к доступу"""
    resource_id: int = Field(gt=0, description="ID ресурса")

