import logging

from fastapi import APIRouter, status, Depends

from bff_service.models.models import (
    RequestAccessRequest,
    RequestAccessResponse,
    RevokePermissionRequest,
    RevokePermissionResponse,
    GetUserPermissionsResponse,
)
from bff_service.services.protocols import UserServiceClientProtocol
from bff_service.dependencies import get_user_service_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/request", response_model=RequestAccessResponse, status_code=status.HTTP_202_ACCEPTED)
async def request_access(
    request: RequestAccessRequest,
    user_service_client: UserServiceClientProtocol = Depends(get_user_service_client),
) -> RequestAccessResponse:
    logger.debug(
        f"Получен запрос на создание заявки: user={request.user_id} "
        f"permission_type={request.permission_type} item_id={request.item_id}"
    )

    response = await user_service_client.request_access(
        user_id=request.user_id,
        permission_type=request.permission_type.value,
        item_id=request.item_id,
    )

    return response


@router.delete("/users/{user_id}/permissions", response_model=RevokePermissionResponse)
async def revoke_permission(
    user_id: int,
    request: RevokePermissionRequest,
    user_service_client: UserServiceClientProtocol = Depends(get_user_service_client),
) -> RevokePermissionResponse:
    logger.debug(
        f"Получен запрос на отзыв права: user={user_id} "
        f"permission_type={request.permission_type} item_id={request.item_id}"
    )

    response = await user_service_client.revoke_permission(
        user_id=user_id,
        permission_type=request.permission_type.value,
        item_id=request.item_id,
    )

    return response


@router.get("/users/{user_id}/permissions", response_model=GetUserPermissionsResponse)
async def get_user_permissions(
    user_id: int,
    user_service_client: UserServiceClientProtocol = Depends(get_user_service_client),
) -> GetUserPermissionsResponse:
    logger.debug(f"Получение прав пользователя: user={user_id}")

    response = await user_service_client.get_user_permissions(user_id=user_id)

    return response
