from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.db.database import db
from access_control_service.models.models import (
    CreateGroupIn,
    CreateGroupOut,
    Group as GroupOut,
    GetGroupAccessesOut
)
from access_control_service.services.group_service import GroupService

router = APIRouter()


@router.post("", response_model=CreateGroupOut, status_code=201)
async def create_group(
    group_in: CreateGroupIn,
    session: AsyncSession = Depends(db.get_db)
):
    """Создание группы прав (служебный эндпоинт)"""
    pass


@router.get("/{group_id}", response_model=GroupOut)
async def get_group(
    group_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Получение группы по ID"""
    pass


@router.get("", response_model=list[GroupOut])
async def get_all_groups(
    session: AsyncSession = Depends(db.get_db)
):
    """Получение всех групп"""
    pass


@router.get("/{group_id}/accesses", response_model=GetGroupAccessesOut)
async def get_accesses_by_group(
    group_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Получение доступов группы"""
    pass


@router.post("/{group_id}/accesses/{access_id}", status_code=204)
async def add_access_to_group(
    group_id: int,
    access_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Добавление доступа к группе"""
    pass


@router.delete("/{group_id}/accesses/{access_id}", status_code=204)
async def remove_access_from_group(
    group_id: int,
    access_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Удаление доступа из группы"""
    pass


@router.delete("/{group_id}", status_code=204)
async def delete_group(
    group_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Удаление группы"""
    pass

