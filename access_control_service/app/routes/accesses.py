from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.db.database import db
from access_control_service.models.models import (
    Access as AccessOut,
    GetAccessGroupsOut,
    Resource as ResourceModel,
)
from access_control_service.services.access_service import AccessService
from access_control_service.app.utils.error_handlers import handle_errors

router = APIRouter()


@router.get("/{access_id}", response_model=AccessOut)
@handle_errors(error_message_prefix="при получении доступа")
async def get_access(
    access_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Получение доступа по ID"""
    access = await AccessService.get_access(session, access_id)
    
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
    session: AsyncSession = Depends(db.get_db)
):
    """Получение всех доступов"""
    accesses = await AccessService.get_all_accesses(session)
    
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


@router.get("/{access_id}/groups", response_model=GetAccessGroupsOut)
@handle_errors(error_message_prefix="при получении групп для доступа")
async def get_groups_by_access(
    access_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Получение групп, содержащих доступ"""
    return await AccessService.get_groups_containing_access(session, access_id)

