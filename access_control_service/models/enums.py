from enum import Enum


class ResourceType(str, Enum):

    API = "API"
    DATABASE = "Database"
    SERVICE = "Service"

