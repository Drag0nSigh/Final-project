from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.dependencies import get_db_session
from access_control_service.models.models import (
    Resource as ResourceOut,
)
from access_control_service.services.resource_service import ResourceService
from access_control_service.utils.error_handlers import handle_errors

router = APIRouter()


@router.get("/{resource_id}", response_model=ResourceOut)
@handle_errors(error_message_prefix="при получении ресурса")
async def get_resource(
    resource_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    resource = await ResourceService.get_resource(session, resource_id)
    return ResourceOut.model_validate(resource)


@router.get("", response_model=list[ResourceOut])
@handle_errors(error_message_prefix="при получении всех ресурсов")
async def get_all_resources(
    session: AsyncSession = Depends(get_db_session)
):
    resources = await ResourceService.get_all_resources(session)
    return [ResourceOut.model_validate(resource) for resource in resources]

