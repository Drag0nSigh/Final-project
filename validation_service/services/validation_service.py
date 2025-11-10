import logging
from typing import Any, Optional
import httpx

from validation_service.models.validation_models import (
    ValidationRequest,
    ValidationResult
)
from validation_service.services.user_service_client import UserServiceClient
from validation_service.services.access_control_client import AccessControlClient

logger = logging.getLogger(__name__)


class ValidationService:
    """Сервис для проверки конфликтов прав"""
    
    def __init__(
        self,
        user_client: UserServiceClient,
        access_control_client: AccessControlClient
    ):
        """Инициализация сервиса валидации"""

        self.user_client = user_client
        self.access_control_client = access_control_client
    
    async def validate(self, request: ValidationRequest) -> ValidationResult:
        """Основной метод валидации"""

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
            
            conflicts = await self.access_control_client.get_conflicts_matrix()
            logger.debug(f"Загружено {len(conflicts)} пар конфликтов")
            
            is_valid, reason = await self._check_conflicts(
                user_groups,
                new_groups,
                conflicts
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
        
        except Exception as e:
            error_msg = f"Неожиданная ошибка при валидации: {str(e)}"
            logger.exception(f"Запрос {request.request_id}: {error_msg}")
            return ValidationResult(
                request_id=request.request_id,
                approved=False,
                reason=error_msg,
                user_id=request.user_id,
                permission_type=request.permission_type,
                item_id=request.item_id
            )
    
    def _extract_group_ids(self, groups_data: list[Any]) -> list[int]:
        """Извлечь ID групп из данных"""

        group_ids = []
        for group in groups_data:
            if isinstance(group, dict):
                group_id = group.get("id")
                if group_id is not None:
                    group_ids.append(int(group_id))
        
        return group_ids
    
    async def _get_user_active_groups(self, user_id: int) -> list[int]:
        """Получить список ID активных групп пользователя"""
        
        groups_data = await self.user_client.get_user_active_groups(user_id)
        return self._extract_group_ids(groups_data)
    
    async def _get_new_groups_for_validation(
        self,
        permission_type: str,
        item_id: int
    ) -> list[int]:
        """Определить новые группы для проверки"""

        if permission_type == "group":
            return [item_id]
        
        elif permission_type == "access":
            groups_data = await self.access_control_client.get_groups_by_access(
                item_id
            )
            return self._extract_group_ids(groups_data)
        
        else:
            logger.warning(
                f"Неизвестный тип разрешения: {permission_type}"
            )
            return []
    
    async def _check_conflicts(
        self,
        user_group_ids: list[int],
        new_group_ids: list[int],
        conflicts: list[dict[str, int]]
    ) -> tuple[bool, Optional[str]]:
        """Проверить конфликты между группами"""
        
        if not user_group_ids or not new_group_ids:
            return True, None
        
        user_groups_set = set(user_group_ids)
        new_groups_set = set(new_group_ids)
        
        for conflict in conflicts:

            group1_id = None
            group2_id = None
            
            if isinstance(conflict, dict):
                group1_id = conflict.get("group1_id")
                group2_id = conflict.get("group2_id")
            
            if group1_id is None or group2_id is None:
                logger.warning(f"Неверный формат конфликта: {conflict}")
                continue
            
            group1_id = int(group1_id)
            group2_id = int(group2_id)
            
            # Проверяем конфликт:
            # Если у пользователя есть group1, а запрашивается group2 -> КОНФЛИКТ
            if group1_id in user_groups_set and group2_id in new_groups_set:
                reason = (
                    f"Конфликт: пользователь имеет группу {group1_id}, "
                    f"запрашивается группа {group2_id}"
                )
                return False, reason
            
            # Если у пользователя есть group2, а запрашивается group1 -> КОНФЛИКТ
            if group2_id in user_groups_set and group1_id in new_groups_set:
                reason = (
                    f"Конфликт: пользователь имеет группу {group2_id}, "
                    f"запрашивается группа {group1_id}"
                )
                return False, reason
        
        return True, None

