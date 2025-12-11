import logging

from fastapi import APIRouter, Depends

from bff_service.models.models import Access
from bff_service.services.protocols import AccessControlClientProtocol
from bff_service.dependencies import get_access_control_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=list[Access])
async def get_all_accesses(
    access_control_client: AccessControlClientProtocol = Depends(get_access_control_client),
) -> list[Access]:
    logger.debug("Получен запрос на получение всех доступов")

    response = await access_control_client.get_all_accesses()

    return response


@router.get("/{access_id}", response_model=Access)
async def get_access(
    access_id: int,
    access_control_client: AccessControlClientProtocol = Depends(get_access_control_client),
) -> Access:
    logger.debug(f"Получен запрос на получение доступа: access_id={access_id}")

    response = await access_control_client.get_access(access_id=access_id)

    return response
