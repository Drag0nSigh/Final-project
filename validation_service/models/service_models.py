from pydantic import BaseModel, ConfigDict, Field


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
    name: str | None = Field(default=None, description="Название группы")
    accesses: list[Access] = Field(default_factory=list, description="Доступы, входящие в группу")


class Conflict(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    group_id1: int = Field(description="ID первой конфликтующей группы")
    group_id2: int = Field(description="ID второй конфликтующей группы")


class GetConflictsResponse(BaseModel):
    conflicts: list[Conflict] = Field(default_factory=list, description="Список конфликтов групп")


class GetGroupAccessesResponse(BaseModel):
    group_id: int = Field(description="ID группы")
    accesses: list[Access] = Field(default_factory=list, description="Доступы, связанные с группой")


class GetAccessGroupsResponse(BaseModel):
    access_id: int = Field(description="ID доступа")
    groups: list[Group] = Field(default_factory=list, description="Группы, содержащие доступ")


class GetUserGroupsResponse(BaseModel):
    groups: list[Group] = Field(default_factory=list, description="Группы пользователя")
