import logging

from fastapi import APIRouter, Depends

from bff_service.models.models import Group
from bff_service.services.protocols import AccessControlClientProtocol
from bff_service.dependencies import get_access_control_client
from bff_service.utils.error_handlers import handle_service_errors

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=list[Group])
@handle_service_errors("Access Control Service")
async def get_all_groups(
    access_control_client: AccessControlClientProtocol = Depends(get_access_control_client),
) -> list[Group]:
    logger.debug("Получен запрос на получение всех групп")

    response = await access_control_client.get_all_groups()

    return response


@router.get("/{group_id}", response_model=Group)
@handle_service_errors("Access Control Service")
async def get_group(
    group_id: int,
    access_control_client: AccessControlClientProtocol = Depends(get_access_control_client),
) -> Group:
    logger.debug(f"Получен запрос на получение группы: group_id={group_id}")

    response = await access_control_client.get_group(group_id=group_id)

    return response

