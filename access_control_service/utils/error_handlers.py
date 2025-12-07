import logging
from functools import wraps
from typing import Callable, TypeVar, ParamSpec

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def handle_errors(
    value_error_status: int = status.HTTP_404_NOT_FOUND,
    error_message_prefix: str = ""
):
    
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except ValueError as exc:
                prefix = error_message_prefix or f"при вызове {func.__name__}"
                logger.warning(f"Ошибка валидации {prefix}: {str(exc)}")
                raise HTTPException(
                    status_code=value_error_status,
                    detail=str(exc)
                ) from exc
            except Exception as exc:
                prefix = error_message_prefix or f"при вызове {func.__name__}"
                logger.exception(f"Ошибка {prefix}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка {prefix}: {str(exc)}"
                ) from exc
        return wrapper
    return decorator

