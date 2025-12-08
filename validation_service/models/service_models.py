from pydantic import BaseModel, ConfigDict, Field


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
    name: str | None = None
    accesses: list[Access] = Field(default_factory=list)


class Conflict(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    group_id1: int
    group_id2: int


class GetConflictsResponse(BaseModel):
    conflicts: list[Conflict] = Field(default_factory=list)


class GetGroupAccessesResponse(BaseModel):
    group_id: int
    accesses: list[Access] = Field(default_factory=list)


class GetAccessGroupsResponse(BaseModel):
    access_id: int
    groups: list[Group] = Field(default_factory=list)


class GetUserGroupsResponse(BaseModel):
    groups: list[Group] = Field(default_factory=list)

