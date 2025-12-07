from enum import Enum


class PermissionType(str, Enum):
    """Тип права доступа."""

    ACCESS = "access"
    GROUP = "group"


class PermissionStatus(str, Enum):
    """Статус права доступа."""

    ACTIVE = "active"
    PENDING = "pending"
    REVOKED = "revoked"
    REJECTED = "rejected"

