from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field


# Pydantic модели для ответов (Output)
class Resource(BaseModel):
    """Модель ресурса"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    type: str
    description: Optional[str] = None


class Access(BaseModel):
    """Модель доступа"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    resources: List[Resource] = Field(default_factory=list)


class Group(BaseModel):
    """Модель группы"""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    accesses: List[Access] = Field(default_factory=list)


class Conflict(BaseModel):
    """Модель конфликта"""
    model_config = ConfigDict(from_attributes=True)
    group_id1: int
    group_id2: int


# Pydantic модели для ввода (Input) - служебные эндпоинты
class CreateResourceIn(BaseModel):
    """Модель для создания ресурса"""
    name: str = Field(..., min_length=1, max_length=100, description="Название ресурса")
    type: Literal["API", "Database", "Service"] = Field(..., description="Тип ресурса")
    description: Optional[str] = Field(None, description="Описание ресурса")


class CreateResourceOut(BaseModel):
    """Модель ответа при создании ресурса"""
    id: int
    name: str
    type: str
    description: Optional[str] = None


class CreateAccessIn(BaseModel):
    """Модель для создания доступа"""
    name: str = Field(..., min_length=1, max_length=100, description="Название доступа")
    resource_ids: List[int] = Field(default_factory=list, description="Список ID ресурсов")


class CreateAccessOut(BaseModel):
    """Модель ответа при создании доступа"""
    id: int
    name: str
    resources: List[Resource] = Field(default_factory=list)


class CreateGroupIn(BaseModel):
    """Модель для создания группы прав"""
    name: str = Field(..., min_length=1, max_length=100, description="Название группы")
    access_ids: List[int] = Field(default_factory=list, description="Список ID доступов")


class CreateGroupOut(BaseModel):
    """Модель ответа при создании группы"""
    id: int
    name: str
    accesses: List[Access] = Field(default_factory=list)


class CreateConflictIn(BaseModel):
    """Модель для создания конфликта между группами"""
    group_id1: int = Field(gt=0, description="ID первой группы")
    group_id2: int = Field(gt=0, description="ID второй группы")


class CreateConflictOut(BaseModel):
    """Модель ответа при создании конфликта"""
    group_id1: int
    group_id2: int


# Модели для API эндпоинтов
class GetRequiredAccessesOut(BaseModel):
    """Модель для получения необходимых доступов для ресурса"""
    resource_id: int
    accesses: List[Access] = Field(default_factory=list)


class GetGroupAccessesOut(BaseModel):
    """Модель для получения доступов группы"""
    group_id: int
    accesses: List[Access] = Field(default_factory=list)


class GetAccessGroupsOut(BaseModel):
    """Модель для получения групп, содержащих доступ"""
    access_id: int
    groups: List[Group] = Field(default_factory=list)


class GetConflictsOut(BaseModel):
    """Модель для получения всех конфликтов"""
    conflicts: List[Conflict] = Field(default_factory=list)


class AddResourceToAccessIn(BaseModel):
    """Модель для добавления ресурса к доступу"""
    resource_id: int = Field(gt=0, description="ID ресурса")

