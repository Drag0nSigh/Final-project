import logging

from fastapi import APIRouter, Depends

from bff_service.models.models import Access
from bff_service.services.access_control_client import AccessControlClient
from bff_service.app.dependencies import get_access_control_client
from bff_service.app.utils.error_handlers import handle_service_errors

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/accesses", response_model=list[Access])
@handle_service_errors("Access Control Service")
async def get_all_accesses(
    access_control_client: AccessControlClient = Depends(get_access_control_client),
):
    """Получение всех доступов"""
    logger.debug("Получен запрос на получение всех доступов")

    response = await access_control_client.get_all_accesses()

    return [Access(**item) for item in response]


@router.get("/accesses/{access_id}", response_model=Access)
@handle_service_errors("Access Control Service")
async def get_access(
    access_id: int,
    access_control_client: AccessControlClient = Depends(get_access_control_client),
):
    """Получение доступа по ID"""
    logger.debug(f"Получен запрос на получение доступа: access_id={access_id}")

    response = await access_control_client.get_access(access_id=access_id)

    return Access(**response)

