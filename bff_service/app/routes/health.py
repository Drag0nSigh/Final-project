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

    return {
        "status": "ready",
        "user_service": "ok",  # TODO: реальная проверка
        "access_control_service": "ok",  # TODO: реальная проверка
        "rabbitmq": "ok"  # TODO: реальная проверка
    }

