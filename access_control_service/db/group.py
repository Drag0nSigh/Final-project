from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from access_control_service.db.base import Base


# Association таблица для Many-to-Many связи Group <-> Access
class GroupAccess(Base):
    """Association таблица между Group и Access"""
    __tablename__ = "group_accesses"
    
    group_id = Column(Integer, ForeignKey("groups.id"), primary_key=True)
    access_id = Column(Integer, ForeignKey("accesses.id"), primary_key=True)


class Group(Base):
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    
    accesses = relationship("Access", secondary="group_accesses", back_populates="groups")
    
    # Связи для конфликтов (через конфликтную таблицу)
    conflicts_as_group1 = relationship(
        "Conflict",
        foreign_keys="Conflict.group_id1",
        back_populates="group1"
    )
    conflicts_as_group2 = relationship(
        "Conflict",
        foreign_keys="Conflict.group_id2",
        back_populates="group2"
    )

