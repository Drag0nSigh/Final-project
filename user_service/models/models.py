from typing import Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    username: str


class UserPermissions(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    permission_type: Literal["access", "group"]
    item_id: int
    status: Literal["active", "pending", "revoked"]
    request_id: int
    assigned_at: datetime
