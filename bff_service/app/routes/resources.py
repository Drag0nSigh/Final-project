import logging

from fastapi import APIRouter, Depends

from bff_service.models.models import Resource
from bff_service.services.protocols import AccessControlClientProtocol
from bff_service.app.dependencies import get_access_control_client
from bff_service.app.utils.error_handlers import handle_service_errors

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/resources", response_model=list[Resource])
@handle_service_errors("Access Control Service")
async def get_all_resources(
    access_control_client: AccessControlClientProtocol = Depends(get_access_control_client),
):
    """Получение всех ресурсов"""
    logger.debug("Получен запрос на получение всех ресурсов")

    response = await access_control_client.get_all_resources()

    return [Resource(**item) for item in response]


@router.get("/resources/{resource_id}", response_model=Resource)
@handle_service_errors("Access Control Service")
async def get_resource(
    resource_id: int,
    access_control_client: AccessControlClientProtocol = Depends(get_access_control_client),
):
    """Получение ресурса по ID"""
    logger.debug(f"Получен запрос на получение ресурса: resource_id={resource_id}")

    response = await access_control_client.get_resource(resource_id=resource_id)

    return Resource(**response)

