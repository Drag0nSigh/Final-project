from enum import Enum


class ResourceType(str, Enum):
    """Тип ресурса."""

    API = "API"
    DATABASE = "Database"
    SERVICE = "Service"

