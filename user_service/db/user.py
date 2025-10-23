from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from userpermission import UserPermission


Base = declarative_base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    username = Column(String(50), unique=True)
    user_permission = relationship("UserPermission", backref="user")

