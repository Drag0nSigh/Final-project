from __future__ import annotations

from functools import lru_cache

from bff_service.config.settings import Settings, get_settings
from bff_service.services.user_service_client import UserServiceClient
from bff_service.services.access_control_client import AccessControlClient
from bff_service.services.protocols import (
    UserServiceClientProtocol,
    AccessControlClientProtocol,
)


@lru_cache(maxsize=1)
def get_settings_dependency() -> Settings:
    return get_settings()


@lru_cache(maxsize=1)
def get_user_service_client() -> UserServiceClientProtocol:
    settings = get_settings_dependency()
    return UserServiceClient(
        base_url=str(settings.user_service_url), timeout=settings.http_timeout
    )


@lru_cache(maxsize=1)
def get_access_control_client() -> AccessControlClientProtocol:
    settings = get_settings_dependency()
    return AccessControlClient(
        base_url=str(settings.access_control_service_url), timeout=settings.http_timeout
    )


async def close_all_clients():
    if get_user_service_client.cache_info().currsize > 0:
        user_client = get_user_service_client()
        await user_client.close()
        get_user_service_client.cache_clear()

    if get_access_control_client.cache_info().currsize > 0:
        access_client = get_access_control_client()
        await access_client.close()
        get_access_control_client.cache_clear()
