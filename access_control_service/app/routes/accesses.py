from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.db.database import db
from access_control_service.models.models import (
    CreateAccessIn,
    CreateAccessOut,
    Access as AccessOut,
    GetAccessGroupsOut,
    AddResourceToAccessIn
)
from access_control_service.services.access_service import AccessService

router = APIRouter()


@router.post("", response_model=CreateAccessOut, status_code=201)
async def create_access(
    access_in: CreateAccessIn,
    session: AsyncSession = Depends(db.get_db)
):
    """Создание доступа (служебный эндпоинт)"""
    pass


@router.get("/{access_id}", response_model=AccessOut)
async def get_access(
    access_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Получение доступа по ID"""
    pass


@router.get("", response_model=list[AccessOut])
async def get_all_accesses(
    session: AsyncSession = Depends(db.get_db)
):
    """Получение всех доступов"""
    pass


@router.get("/{access_id}/groups", response_model=GetAccessGroupsOut)
async def get_groups_by_access(
    access_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Получение групп, содержащих доступ"""
    pass


@router.post("/{access_id}/resources", response_model=AccessOut)
async def add_resource_to_access(
    access_id: int,
    resource_data: AddResourceToAccessIn,
    session: AsyncSession = Depends(db.get_db)
):
    """Добавление ресурса к доступу"""
    pass


@router.delete("/{access_id}/resources/{resource_id}", status_code=204)
async def remove_resource_from_access(
    access_id: int,
    resource_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Удаление ресурса из доступа"""
    pass


@router.delete("/{access_id}", status_code=204)
async def delete_access(
    access_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Удаление доступа"""
    pass

