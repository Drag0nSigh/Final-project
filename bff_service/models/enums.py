from enum import Enum


class PermissionType(str, Enum):
    ACCESS = "access"
    GROUP = "group"


class PermissionStatus(str, Enum):
    ACTIVE = "active"
    PENDING = "pending"
    REVOKED = "revoked"
    REJECTED = "rejected"

