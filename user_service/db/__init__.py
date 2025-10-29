# Импорт всех моделей для регистрации в SQLAlchemy
from user_service.db.base import Base
from user_service.db.user import User
from user_service.db.userpermission import UserPermission

__all__ = ["Base", "User", "UserPermission"]

