"""
RabbitMQ Consumer для обработки результатов валидации из Validation Service

Этот модуль обрабатывает сообщения из очереди result_queue,
полученные от Validation Service после проверки конфликтов прав.
"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()


async def on_validation_result(message: Dict[str, Any]):
    """
    Обработчик результата валидации из RabbitMQ
    
    Получает сообщение из result_queue с результатом проверки конфликтов:
    {
        "request_id": "uuid",
        "user_id": 123,
        "type": "group",
        "item_id": 5,
        "status": "approved" или "rejected",
        "reason": "причина отклонения (опционально)"
    }
    
    Действия:
    - Если approved: вызывает User Service для активации заявки
    - Если rejected: вызывает User Service для отклонения заявки
    - Инвалидирует кэш пользователя
    """
    # TODO: Реализация
    # 1. Парсинг сообщения из RabbitMQ
    # 2. Вызвать User Service API: PUT /permissions/{request_id}/status
    #    с body: {"status": "active" или "rejected", "reason": ...}
    # 3. Инвалидировать кэш Redis (user:{user_id}:groups)
    # 4. Логировать результат
    # 5. Обработать ошибки (retry при недоступности User Service)
    pass


# TODO: Настроить RabbitMQ consumer в lifespan
# async def start_rabbitmq_consumer():
#     """Запуск consumer для result_queue"""
#     # await rabbitmq.consume("result_queue", on_validation_result)
#     pass

