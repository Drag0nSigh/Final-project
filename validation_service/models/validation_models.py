"""
Pydantic модели для RabbitMQ сообщений Validation Service

Модели для обмена данными между сервисами через RabbitMQ:
- ValidationRequest: запрос на валидацию из validation_queue
- ValidationResult: результат валидации для отправки в result_queue
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ValidationRequest(BaseModel):
    """Модель запроса на валидацию из RabbitMQ"""
    
    user_id: int = Field(gt=0, description="ID пользователя")
    permission_type: Literal["access", "group"] = Field(
        description="Тип права: 'access' - доступ, 'group' - группа"
    )
    item_id: int = Field(gt=0, description="ID доступа или группы")
    request_id: str = Field(description="UUID заявки для отслеживания")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 123,
                "permission_type": "group",
                "item_id": 2,
                "request_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class ValidationResult(BaseModel):
    """Модель результата валидации для отправки в RabbitMQ"""
    
    request_id: str = Field(description="UUID заявки")
    approved: bool = Field(description="Одобрено или отклонено")
    reason: Optional[str] = Field(
        default=None,
        description="Причина отклонения (если approved=False)"
    )
    user_id: int = Field(description="ID пользователя")
    permission_type: Literal["access", "group"] = Field(
        description="Тип права: 'access' - доступ, 'group' - группа"
    )
    item_id: int = Field(description="ID доступа или группы")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "550e8400-e29b-41d4-a716-446655440000",
                "approved": False,
                "reason": "Conflict: User has group 2 (Developer), requesting group 1 (Owner)",
                "user_id": 123,
                "permission_type": "group",
                "item_id": 2
            }
        }

