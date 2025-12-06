import logging
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from sqlalchemy import text

from access_control_service.app.dependencies import get_database, get_redis_client

logger = logging.getLogger(__name__)
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
    """Проверка готовности сервиса (БД и Redis)"""
    checks = {
        "db": False,
        "redis": False
    }
    
    db = get_database()
    redis_client = get_redis_client()
    
    try:
        if db.engine is None:
            logger.warning("БД не инициализирована")
            checks["db"] = False
        else:
            async with db.engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                result.scalar()
                checks["db"] = True
    except Exception as exc:
        logger.error(f"Ошибка проверки БД: {exc}")
        checks["db"] = False
    
    try:
        redis_conn = redis_client.connection
        await redis_conn.ping()
        checks["redis"] = True
    except Exception as exc:
        logger.error(f"Ошибка проверки Redis: {exc}")
        checks["redis"] = False
    
    if not all(checks.values()):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "not ready",
                "checks": checks
            }
        )
    
    return {
        "status": "ready",
        "checks": checks
    }

