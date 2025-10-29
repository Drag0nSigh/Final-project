from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from access_control_service.db.base import Base


class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    type = Column(String(50), nullable=False) 
    description = Column(Text, nullable=True)
    
    accesses = relationship("Access", secondary="access_resources", back_populates="resources")

