from fastapi import APIRouter, HTTPException, status, Depends

from user_service.models.models import (
    CreateUserRequest,
    CreateUserResponse
)
from user_service.dependencies import get_user_repository
from user_service.repositories.protocols import UserRepositoryProtocol
from user_service.db.user import User

router = APIRouter()


@router.post("/users", response_model=CreateUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: CreateUserRequest,
    user_repository: UserRepositoryProtocol = Depends(get_user_repository),
):

    existing_user = await user_repository.find_by_username(user_data.username)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username '{user_data.username}' already exists"
        )

    new_user = User(username=user_data.username)
    new_user = await user_repository.save(new_user)

    return CreateUserResponse(id=new_user.id, username=new_user.username)
