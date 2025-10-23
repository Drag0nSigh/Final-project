from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from user import User

Base = declarative_base


class UserPermission(Base):
    __tablename__ = "userpermission"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey="user.user_id")
