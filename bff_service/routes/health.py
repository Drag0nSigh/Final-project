from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "service": "bff-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/ready")
async def readiness_check():

    return {
        "status": "ready",
        "user_service": "ok",  
        "access_control_service": "ok",
        "rabbitmq": "ok" 
    }

