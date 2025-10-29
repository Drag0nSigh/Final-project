from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from access_control_service.db.base import Base


# Association таблица для Many-to-Many связи Access <-> Resource
class AccessResource(Base):
    """Association таблица между Access и Resource"""
    __tablename__ = "access_resources"
    
    access_id = Column(Integer, ForeignKey("accesses.id"), primary_key=True)
    resource_id = Column(Integer, ForeignKey("resources.id"), primary_key=True)


class Access(Base):
    __tablename__ = "accesses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    
    resources = relationship("Resource", secondary="access_resources", back_populates="accesses")
    
    groups = relationship("Group", secondary="group_accesses", back_populates="accesses")

