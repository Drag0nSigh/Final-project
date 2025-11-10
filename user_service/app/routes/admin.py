from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from user_service.models.models import (
    CreateUserIn,
    CreateUserOut
)
from user_service.db.database import db
from user_service.db.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/users", response_model=CreateUserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: CreateUserIn, session: AsyncSession = Depends(db.get_db)):
    """
    Служебный эндпоинт для создания пользователя
    
    Создает нового пользователя в системе.
    Используется для начальной настройки или административных задач.
    """
    stmt = select(User).where(User.username == user_data.username)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username '{user_data.username}' already exists"
        )
    
    new_user = User(username=user_data.username)
    session.add(new_user)
    await session.flush()
    
    await session.refresh(new_user)
    
    return CreateUserOut(id=new_user.id, username=new_user.username)



