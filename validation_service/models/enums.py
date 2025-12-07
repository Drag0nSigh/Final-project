from enum import Enum


class PermissionType(str, Enum):
    """Тип права доступа."""

    ACCESS = "access"
    GROUP = "group"

