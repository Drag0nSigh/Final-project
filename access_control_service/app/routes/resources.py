from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.db.database import db
from access_control_service.models.models import (
    CreateResourceIn,
    CreateResourceOut,
    Resource as ResourceOut,
    GetRequiredAccessesOut
)
from access_control_service.services.resource_service import ResourceService

router = APIRouter()


@router.post("", response_model=CreateResourceOut, status_code=201)
async def create_resource(
    resource_in: CreateResourceIn,
    session: AsyncSession = Depends(db.get_db)
):
    """Создание ресурса (служебный эндпоинт)"""
    pass


@router.get("/{resource_id}", response_model=ResourceOut)
async def get_resource(
    resource_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Получение ресурса по ID"""
    pass


@router.get("", response_model=list[ResourceOut])
async def get_all_resources(
    session: AsyncSession = Depends(db.get_db)
):
    """Получение всех ресурсов"""
    pass


@router.get("/{resource_id}/required_accesses", response_model=GetRequiredAccessesOut)
async def get_required_accesses_for_resource(
    resource_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Получение необходимых доступов для ресурса (ТЗ п.4)"""
    pass


@router.delete("/{resource_id}", status_code=204)
async def delete_resource(
    resource_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Удаление ресурса"""
    pass

