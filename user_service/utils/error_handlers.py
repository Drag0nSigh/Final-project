import logging
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def handle_errors(error_message: str):
    """Декоратор для обработки ошибок в эндпоинтах."""
    
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as exc:
                logger.exception(f"Ошибка при вызове {func.__name__}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_message,
                ) from exc
        return wrapper
    return decorator

