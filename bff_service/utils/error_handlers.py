import logging
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

import httpx
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def handle_service_errors(service_name: str):
    """
    Декоратор для обработки ошибок при взаимодействии с внешними сервисами.
    
    Args:
        service_name: Название сервиса (например, "User Service" или "Access Control Service")
    
    Обрабатывает:
        - httpx.HTTPStatusError: пробрасывает статус код от сервиса
        - httpx.RequestError: возвращает 503 если сервис недоступен
        - Exception: возвращает 500 для неожиданных ошибок
        - HTTPException: пробрасывает как есть
    """
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except httpx.HTTPStatusError as e:
                logger.warning(
                    f"{service_name} вернул ошибку: {e.response.status_code} - {e.response.text}"
                )
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail=e.response.text or f"Ошибка при обработке запроса в {service_name}",
                ) from e
            except httpx.RequestError as e:
                logger.error(f"Ошибка при запросе к {service_name}: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"{service_name} недоступен",
                ) from e
            except Exception as exc:
                logger.exception(f"Неожиданная ошибка при вызове {func.__name__} через {service_name}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Внутренняя ошибка при обработке запроса",
                ) from exc
        return wrapper
    return decorator

