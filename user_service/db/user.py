from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from user_service.db.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    
    # Связь с правами пользователя
    permissions = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan")

