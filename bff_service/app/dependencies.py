from functools import lru_cache

from bff_service.config.settings import Settings, get_settings
from bff_service.services.user_service_client import UserServiceClient
from bff_service.services.access_control_client import AccessControlClient


@lru_cache(maxsize=1)
def get_settings_dependency() -> Settings:
    """Возвращает настройки для использования в Depends()."""
    return get_settings()


_user_service_client: UserServiceClient | None = None
_access_control_client: AccessControlClient | None = None


def get_user_service_client() -> UserServiceClient:
    """Возвращает HTTP клиент для User Service (singleton)."""
    global _user_service_client
    if _user_service_client is None:
        settings = get_settings()
        _user_service_client = UserServiceClient(
            base_url=str(settings.user_service_url), timeout=settings.http_timeout
        )
    return _user_service_client


def get_access_control_client() -> AccessControlClient:
    """Возвращает HTTP клиент для Access Control Service (singleton)."""
    global _access_control_client
    if _access_control_client is None:
        settings = get_settings()
        _access_control_client = AccessControlClient(
            base_url=str(settings.access_control_service_url), timeout=settings.http_timeout
        )
    return _access_control_client


async def close_all_clients():
    """Закрывает все HTTP клиенты при завершении приложения."""
    global _user_service_client, _access_control_client
    if _user_service_client is not None:
        await _user_service_client.close()
        _user_service_client = None
    if _access_control_client is not None:
        await _access_control_client.close()
        _access_control_client = None

