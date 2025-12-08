from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from sqlalchemy import text

from user_service.dependencies import get_database, get_redis_client, get_rabbitmq_manager

router = APIRouter()


@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "service": "user-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ready")
async def readiness_check():

    db = get_database()
    redis_client = get_redis_client()
    rabbitmq_manager = get_rabbitmq_manager()

    checks = {
        "db": "unknown",
        "redis": "unknown",
        "rabbitmq": "unknown",
    }
    all_ok = True

    try:
        if db.engine is None:
            checks["db"] = "not_initialized"
            all_ok = False
        else:
            async with db.engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                result.scalar()
            checks["db"] = "ok"
    except Exception as exc:
        checks["db"] = f"error: {str(exc)}"
        all_ok = False

    try:
        await redis_client.connection.ping()
        checks["redis"] = "ok"
    except RuntimeError:
        checks["redis"] = "not_connected"
        all_ok = False
    except Exception as exc:
        checks["redis"] = f"error: {str(exc)}"
        all_ok = False

    try:
        if not rabbitmq_manager.is_connected:
            checks["rabbitmq"] = "not_connected"
            all_ok = False
        elif rabbitmq_manager.channel is None or rabbitmq_manager.channel.is_closed:
            checks["rabbitmq"] = "channel_closed"
            all_ok = False
        else:
            checks["rabbitmq"] = "ok"
    except Exception as exc:
        checks["rabbitmq"] = f"error: {str(exc)}"
        all_ok = False

    response = {
        "status": "ready" if all_ok else "not_ready",
        "timestamp": datetime.utcnow().isoformat(),
        **checks,
    }

    if not all_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response,
        )

    return response

