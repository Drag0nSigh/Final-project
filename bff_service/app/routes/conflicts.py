import logging

from fastapi import APIRouter, Depends

from bff_service.models.models import GetConflictsOut
from bff_service.services.protocols import AccessControlClientProtocol
from bff_service.app.dependencies import get_access_control_client
from bff_service.app.utils.error_handlers import handle_service_errors

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/conflicts", response_model=GetConflictsOut)
@handle_service_errors("Access Control Service")
async def get_all_conflicts(
    access_control_client: AccessControlClientProtocol = Depends(get_access_control_client),
):
    """Получение всех конфликтов"""
    logger.debug("Получен запрос на получение всех конфликтов")

    response = await access_control_client.get_conflicts()

    return GetConflictsOut(**response)

