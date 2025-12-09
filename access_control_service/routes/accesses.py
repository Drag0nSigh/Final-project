from fastapi import APIRouter, Depends, status

from access_control_service.dependencies import get_access_service
from access_control_service.models.models import (
    Access as AccessOut,
    GetAccessGroupsResponse,
    Resource as ResourceModel,
)
from access_control_service.services.protocols import AccessServiceProtocol

router = APIRouter()


@router.get("/{access_id}", response_model=AccessOut)
async def get_access(
    access_id: int,
    access_service: AccessServiceProtocol = Depends(get_access_service),
):
    access = await access_service.get_access(access_id)
    
    resources_out = [
        ResourceModel(
            id=res.id,
            name=res.name,
            type=res.type,
            description=res.description,
        )
        for res in access.resources
    ]
    
    return AccessOut(
        id=access.id,
        name=access.name,
        resources=resources_out,
    )


@router.get("", response_model=list[AccessOut])
async def get_all_accesses(
    access_service: AccessServiceProtocol = Depends(get_access_service),
):
    accesses = await access_service.get_all_accesses()

    return [
        AccessOut(
            id=access.id,
            name=access.name,
            resources=[
                ResourceModel(
                    id=res.id,
                    name=res.name,
                    type=res.type,
                    description=res.description,
                )
                for res in access.resources
            ],
        )
        for access in accesses
    ]


@router.get("/{access_id}/groups", response_model=GetAccessGroupsResponse)
async def get_groups_by_access(
    access_id: int,
    access_service: AccessServiceProtocol = Depends(get_access_service),
):
    return await access_service.get_groups_containing_access(access_id)

