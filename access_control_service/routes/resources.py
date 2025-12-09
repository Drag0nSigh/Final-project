from fastapi import APIRouter, Depends

from access_control_service.dependencies import get_resource_service
from access_control_service.models.models import (
    Resource as ResourceOut,
)
from access_control_service.services.protocols import ResourceServiceProtocol

router = APIRouter()


router = APIRouter()


@router.get("/{resource_id}", response_model=ResourceOut)
async def get_resource(
    resource_id: int,
    resource_service: ResourceServiceProtocol = Depends(get_resource_service),
):
    resource = await resource_service.get_resource(resource_id)
    return ResourceOut.model_validate(resource)


@router.get("", response_model=list[ResourceOut])
async def get_all_resources(
    resource_service: ResourceServiceProtocol = Depends(get_resource_service),
):
    resources = await resource_service.get_all_resources()
    return [ResourceOut.model_validate(resource) for resource in resources]

