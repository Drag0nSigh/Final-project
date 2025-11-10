from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from user_service.db.base import Base


class UserPermission(Base):
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    permission_type = Column(String(20), nullable=False)
    item_id = Column(Integer, nullable=False)
    item_name = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    request_id = Column(String(36), nullable=False, unique=True, index=True)  # UUID для трекинга
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    
    # Связь с пользователем
    user = relationship("User", back_populates="permissions")
    
    # Предотвращение дублей: один пользователь не может иметь два одинаковых права
    __table_args__ = (
        UniqueConstraint('user_id', 'permission_type', 'item_id', name='unique_user_permission'),
    )
