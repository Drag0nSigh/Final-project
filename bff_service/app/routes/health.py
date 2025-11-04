from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Проверка работоспособности BFF Service"""
    return {
        "status": "healthy",
        "service": "bff-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ready")
async def readiness_check():
    """Проверка готовности BFF Service (подключения к другим сервисам)"""
    # TODO: Реализация проверки подключений
    # 1. Проверить подключение к User Service
    # 2. Проверить подключение к Access Control Service
    # 3. Проверить подключение к RabbitMQ
    # 4. Проверить подключение к Redis (если используется)
    return {
        "status": "ready",
        "user_service": "ok",  # TODO: реальная проверка
        "access_control_service": "ok",  # TODO: реальная проверка
        "rabbitmq": "ok"  # TODO: реальная проверка
    }

