from fastapi import APIRouter, Depends, status

from access_control_service.dependencies import get_access_service
from access_control_service.models.models import (
    Access as AccessOut,
    GetAccessGroupsResponse,
    Resource as ResourceModel,
)
from access_control_service.services.protocols import AccessServiceProtocol
from access_control_service.utils.error_handlers import handle_errors

router = APIRouter()


@router.get("/{access_id}", response_model=AccessOut)
@handle_errors(error_message_prefix="при получении доступа")
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
@handle_errors(error_message_prefix="при получении всех доступов")
async def get_all_accesses(
    access_service: AccessServiceProtocol = Depends(get_access_service),
):
    accesses = await access_service.get_all_accesses()
    
    result = []
    for access in accesses:
        resources_out = [
            ResourceModel(
                id=res.id,
                name=res.name,
                type=res.type,
                description=res.description,
            )
            for res in access.resources
        ]
        result.append(
            AccessOut(
                id=access.id,
                name=access.name,
                resources=resources_out,
            )
        )
    
    return result


@router.get("/{access_id}/groups", response_model=GetAccessGroupsResponse)
@handle_errors(error_message_prefix="при получении групп для доступа")
async def get_groups_by_access(
    access_id: int,
    access_service: AccessServiceProtocol = Depends(get_access_service),
):
    return await access_service.get_groups_containing_access(access_id)

