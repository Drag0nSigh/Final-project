from pydantic import BaseModel, ConfigDict, Field

from access_control_service.models.enums import ResourceType


class Resource(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    type: str
    description: str | None = None


class Access(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    resources: list[Resource] = Field(default_factory=list)


class Group(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    accesses: list[Access] = Field(default_factory=list)


class Conflict(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    group_id1: int
    group_id2: int


class CreateResourceRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название ресурса")
    type: ResourceType = Field(..., description="Тип ресурса")
    description: str | None = Field(None, description="Описание ресурса")


class CreateResourceResponse(BaseModel):
    id: int
    name: str
    type: str
    description: str | None = None


class CreateAccessRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название доступа")
    resource_ids: list[int] = Field(default_factory=list, description="Список ID ресурсов")


class CreateAccessResponse(BaseModel):
    id: int
    name: str
    resources: list[Resource] = Field(default_factory=list)


class CreateGroupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название группы")
    access_ids: list[int] = Field(default_factory=list, description="Список ID доступов")


class CreateGroupResponse(BaseModel):
    id: int
    name: str
    accesses: list[Access] = Field(default_factory=list)


class CreateConflictRequest(BaseModel):
    group_id1: int = Field(gt=0, description="ID первой группы")
    group_id2: int = Field(gt=0, description="ID второй группы")


class CreateConflictResponse(BaseModel):
    group_id1: int
    group_id2: int


class DeleteConflictRequest(BaseModel):
    group_id1: int = Field(gt=0, description="ID первой группы")
    group_id2: int = Field(gt=0, description="ID второй группы")


class GetGroupAccessesResponse(BaseModel):
    group_id: int
    accesses: list[Access] = Field(default_factory=list)


class GetAccessGroupsResponse(BaseModel):
    access_id: int
    groups: list[Group] = Field(default_factory=list)


class GetConflictsResponse(BaseModel):
    conflicts: list[Conflict] = Field(default_factory=list)


class AddResourceToAccessRequest(BaseModel):
    resource_id: int = Field(gt=0, description="ID ресурса")

