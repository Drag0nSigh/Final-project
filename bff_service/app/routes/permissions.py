import logging

from fastapi import APIRouter, status, Depends

from bff_service.models.models import (
    RequestAccessIn,
    RequestAccessOut,
    RevokePermissionIn,
    RevokePermissionOut,
    GetUserPermissionsOut,
)
from bff_service.services.user_service_client import UserServiceClient
from bff_service.app.dependencies import get_user_service_client
from bff_service.app.utils.error_handlers import handle_service_errors

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/request", response_model=RequestAccessOut, status_code=status.HTTP_202_ACCEPTED)
@handle_service_errors("User Service")
async def request_access(
    request: RequestAccessIn,
    user_service_client: UserServiceClient = Depends(get_user_service_client),
):
    """Создание заявки на получение доступа или группы прав"""
    logger.debug(
        f"Получен запрос на создание заявки: user={request.user_id} "
        f"permission_type={request.permission_type} item_id={request.item_id}"
    )

    response = await user_service_client.request_access(
        user_id=request.user_id,
        permission_type=request.permission_type,
        item_id=request.item_id,
    )

    return RequestAccessOut(
        status=response.get("status", "accepted"),
        request_id=response.get("request_id"),
    )


@router.delete("/users/{user_id}/permissions", response_model=RevokePermissionOut)
@handle_service_errors("User Service")
async def revoke_permission(
    user_id: int,
    request: RevokePermissionIn,
    user_service_client: UserServiceClient = Depends(get_user_service_client),
):
    """Отзыв права у пользователя"""
    logger.debug(
        f"Получен запрос на отзыв права: user={user_id} "
        f"permission_type={request.permission_type} item_id={request.item_id}"
    )

    response = await user_service_client.revoke_permission(
        user_id=user_id,
        permission_type=request.permission_type,
        item_id=request.item_id,
    )

    return RevokePermissionOut(**response)


@router.get("/users/{user_id}/permissions", response_model=GetUserPermissionsOut)
@handle_service_errors("User Service")
async def get_user_permissions(
    user_id: int,
    user_service_client: UserServiceClient = Depends(get_user_service_client),
):
    """Получение всех прав пользователя"""
    logger.debug(f"Получение прав пользователя: user={user_id}")

    response = await user_service_client.get_user_permissions(user_id=user_id)

    return GetUserPermissionsOut(**response)

