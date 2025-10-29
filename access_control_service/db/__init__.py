# Импорт всех моделей для регистрации в SQLAlchemy
from access_control_service.db.base import Base
from access_control_service.db.resource import Resource
from access_control_service.db.access import Access, AccessResource
from access_control_service.db.group import Group, GroupAccess
from access_control_service.db.conflict import Conflict

__all__ = [
    "Base",
    "Resource",
    "Access",
    "AccessResource",
    "Group",
    "GroupAccess",
    "Conflict"
]

