import logging

from fastapi import APIRouter, Depends

from bff_service.models.models import GetConflictsResponse
from bff_service.services.protocols import AccessControlClientProtocol
from bff_service.dependencies import get_access_control_client
from bff_service.utils.error_handlers import handle_service_errors

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=GetConflictsResponse)
@handle_service_errors("Access Control Service")
async def get_all_conflicts(
    access_control_client: AccessControlClientProtocol = Depends(get_access_control_client),
) -> GetConflictsResponse:
    logger.debug("Получен запрос на получение всех конфликтов")

    response = await access_control_client.get_conflicts()

    return response

