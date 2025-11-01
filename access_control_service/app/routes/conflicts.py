from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from access_control_service.db.database import db
from access_control_service.models.models import (
    CreateConflictIn,
    CreateConflictOut,
    Conflict as ConflictOut,
    GetConflictsOut
)
from access_control_service.services.conflict_service import ConflictService

router = APIRouter()


@router.post("", response_model=list[CreateConflictOut], status_code=201)
async def create_conflict(
    conflict_in: CreateConflictIn,
    session: AsyncSession = Depends(db.get_db)
):
    """Создание конфликта между группами (служебный эндпоинт).
    
    Автоматически создает симметричную пару (group1,group2) и (group2,group1)
    """
    pass


@router.get("", response_model=GetConflictsOut)
async def get_all_conflicts(
    session: AsyncSession = Depends(db.get_db)
):
    """Получение всех конфликтов (для Validation Service)"""
    pass


@router.get("/{group_id}", response_model=list[ConflictOut])
async def get_conflicts_by_group(
    group_id: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Получение конфликтов для конкретной группы"""
    pass


@router.delete("", status_code=204)
async def delete_conflict(
    group_id1: int,
    group_id2: int,
    session: AsyncSession = Depends(db.get_db)
):
    """Удаление конфликта между группами"""
    pass

