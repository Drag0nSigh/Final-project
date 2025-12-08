from pydantic import BaseModel, Field, ConfigDict

from validation_service.models.enums import PermissionType


class ValidationRequest(BaseModel):
    
    user_id: int = Field(gt=0, description="ID пользователя")
    permission_type: PermissionType = Field(
        description="Тип права: 'access' - доступ, 'group' - группа"
    )
    item_id: int = Field(gt=0, description="ID доступа или группы")
    request_id: str = Field(description="UUID заявки для отслеживания")
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "user_id": 123,
                "permission_type": "group",
                "item_id": 2,
                "request_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    )

class ValidationResult(BaseModel):
    
    request_id: str = Field(description="UUID заявки")
    approved: bool = Field(description="Одобрено или отклонено")
    reason: str | None = Field(
        default=None,
        description="Причина отклонения (если approved=False)"
    )
    user_id: int = Field(description="ID пользователя")
    permission_type: PermissionType = Field(
        description="Тип права: 'access' - доступ, 'group' - группа"
    )
    item_id: int = Field(description="ID доступа или группы")
    
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "approved": False,
                "reason": "Conflict: User has group 2 (Developer), requesting group 1 (Owner)",
                "user_id": 123,
                "permission_type": "group",
                "item_id": 2
            }
        }
    )

