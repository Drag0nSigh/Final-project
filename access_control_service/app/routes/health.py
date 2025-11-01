from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("")
async def health_check():
    """Проверка работоспособности сервиса"""
    return {
        "status": "healthy",
        "service": "access-control-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ready")
async def readiness_check():
    """Проверка готовности сервиса (БД)"""
    # TODO: проверка подключений
    return {
        "status": "ready",
        "db": "ok"  # TODO: реальная проверка
    }

