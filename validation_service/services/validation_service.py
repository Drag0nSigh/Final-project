import logging
import httpx

from validation_service.models.validation_models import (
    ValidationRequest,
    ValidationResult
)
from validation_service.models.service_models import (
    Group,
    Conflict,
)
from validation_service.services.protocols import (
    UserServiceClientProtocol,
    AccessControlClientProtocol,
)

logger = logging.getLogger(__name__)


class ValidationService:

    def __init__(
        self,
        user_client: UserServiceClientProtocol,
        access_control_client: AccessControlClientProtocol
    ):

        self._user_client = user_client
        self._access_control_client = access_control_client

    async def validate(self, request: ValidationRequest) -> ValidationResult:

        try:
            user_groups = await self._get_user_active_groups(request.user_id)
            logger.debug(
                f"Пользователь {request.user_id} имеет активные группы: {user_groups}"
            )

            new_groups = await self._get_new_groups_for_validation(
                request.permission_type,
                request.item_id
            )
            logger.debug(
                f"Запрос {request.request_id}: новые группы для проверки: {new_groups}"
            )

            if not new_groups:
                return ValidationResult(
                    request_id=request.request_id,
                    approved=False,
                    reason=f"Не найдено групп для {request.permission_type} с ID {request.item_id}",
                    user_id=request.user_id,
                    permission_type=request.permission_type,
                    item_id=request.item_id
                )

            conflicts_response = await self._access_control_client.get_conflicts_matrix()
            logger.debug(f"Загружено {len(conflicts_response.conflicts)} пар конфликтов")

            is_valid, reason = await self._check_conflicts(
                user_groups,
                new_groups,
                conflicts_response.conflicts
            )

            if is_valid:
                logger.debug(
                    f"Запрос {request.request_id} одобрен: "
                    f"пользователь {request.user_id}, {request.permission_type} {request.item_id}"
                )
                return ValidationResult(
                    request_id=request.request_id,
                    approved=True,
                    reason=None,
                    user_id=request.user_id,
                    permission_type=request.permission_type,
                    item_id=request.item_id
                )
            else:
                logger.warning(
                    f"Запрос {request.request_id} отклонен: {reason}"
                )
                return ValidationResult(
                    request_id=request.request_id,
                    approved=False,
                    reason=reason,
                    user_id=request.user_id,
                    permission_type=request.permission_type,
                    item_id=request.item_id
                )

        except httpx.HTTPError as e:
            error_msg = f"Ошибка при получении данных: {str(e)}"
            logger.error(f"Запрос {request.request_id}: {error_msg}")
            return ValidationResult(
                request_id=request.request_id,
                approved=False,
                reason=error_msg,
                user_id=request.user_id,
                permission_type=request.permission_type,
                item_id=request.item_id
            )

    def _extract_group_ids(self, groups: list[Group]) -> list[int]:
        return [group.id for group in groups]

    async def _get_user_active_groups(self, user_id: int) -> list[int]:
        response = await self._user_client.get_user_active_groups(user_id)
        return self._extract_group_ids(response.groups)

    async def _get_new_groups_for_validation(
        self,
        permission_type: str,
        item_id: int
    ) -> list[int]:

        if permission_type == "group":
            return [item_id]

        elif permission_type == "access":
            response = await self._access_control_client.get_groups_by_access(item_id)
            return self._extract_group_ids(response.groups)

        else:
            logger.warning(
                f"Неизвестный тип разрешения: {permission_type}"
            )
            return []

    async def _check_conflicts(
        self,
        user_group_ids: list[int],
        new_group_ids: list[int],
        conflicts: list[Conflict]
    ) -> tuple[bool, str | None]:

        if not user_group_ids or not new_group_ids:
            return True, None

        user_groups_set = set(user_group_ids)
        new_groups_set = set(new_group_ids)

        for conflict in conflicts:
            group1_id = conflict.group_id1
            group2_id = conflict.group_id2

            if group1_id in user_groups_set and group2_id in new_groups_set:
                return False, (
                    f"Конфликт: пользователь имеет группу {group1_id}, "
                    f"запрашивается группа {group2_id}"
                )

            if group2_id in user_groups_set and group1_id in new_groups_set:
                return False, (
                    f"Конфликт: пользователь имеет группу {group2_id}, "
                    f"запрашивается группа {group1_id}"
                )

        return True, None
