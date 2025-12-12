from pydantic import BaseModel, ConfigDict, Field

from access_control_service.models.enums import ResourceType


class Resource(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(description="ID ресурса")
    name: str = Field(description="Название ресурса")
    type: str = Field(description="Тип ресурса")
    description: str | None = Field(default=None, description="Описание ресурса")


class Access(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(description="ID доступа")
    name: str = Field(description="Название доступа")
    resources: list[Resource] = Field(default_factory=list, description="Ресурсы, связанные с доступом")


class Group(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(description="ID группы")
    name: str = Field(description="Название группы")
    accesses: list[Access] = Field(default_factory=list, description="Доступы, входящие в группу")


class Conflict(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    group_id1: int = Field(description="ID первой конфликтующей группы")
    group_id2: int = Field(description="ID второй конфликтующей группы")


class CreateResourceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название ресурса")
    type: ResourceType = Field(..., description="Тип ресурса")
    description: str | None = Field(None, description="Описание ресурса")


class CreateResourceResponse(BaseModel):
    id: int = Field(description="ID созданного ресурса")
    name: str = Field(description="Название созданного ресурса")
    type: str = Field(description="Тип созданного ресурса")
    description: str | None = Field(default=None, description="Описание ресурса")


class CreateAccessRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название доступа")
    resource_ids: list[int] = Field(default_factory=list, description="Список ID ресурсов")


class CreateAccessResponse(BaseModel):
    id: int = Field(description="ID созданного доступа")
    name: str = Field(description="Название созданного доступа")
    resources: list[Resource] = Field(default_factory=list, description="Ресурсы, привязанные к доступу")


class CreateGroupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название группы")
    access_ids: list[int] = Field(default_factory=list, description="Список ID доступов")


class CreateGroupResponse(BaseModel):
    id: int = Field(description="ID созданной группы")
    name: str = Field(description="Название созданной группы")
    accesses: list[Access] = Field(default_factory=list, description="Доступы, входящие в группу")


class CreateConflictRequest(BaseModel):
    group_id1: int = Field(gt=0, description="ID первой группы")
    group_id2: int = Field(gt=0, description="ID второй группы")


class CreateConflictResponse(BaseModel):
    group_id1: int = Field(description="ID первой конфликтующей группы")
    group_id2: int = Field(description="ID второй конфликтующей группы")


class DeleteConflictRequest(BaseModel):
    group_id1: int = Field(gt=0, description="ID первой группы")
    group_id2: int = Field(gt=0, description="ID второй группы")


class GetGroupAccessesResponse(BaseModel):
    group_id: int = Field(description="ID группы")
    accesses: list[Access] = Field(default_factory=list, description="Доступы, связанные с группой")


class GetAccessGroupsResponse(BaseModel):
    access_id: int = Field(description="ID доступа")
    groups: list[Group] = Field(default_factory=list, description="Группы, содержащие доступ")


class GetConflictsResponse(BaseModel):
    conflicts: list[Conflict] = Field(default_factory=list, description="Список конфликтов групп")


class AddResourceToAccessRequest(BaseModel):
    resource_id: int = Field(gt=0, description="ID ресурса")
