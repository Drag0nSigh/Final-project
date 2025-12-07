from __future__ import annotations

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from access_control_service.db.base import Base


class AccessResource(Base):
    """Association таблица между Access и Resource"""
    __tablename__ = "access_resources"
    
    access_id: Mapped[int] = mapped_column(ForeignKey("accesses.id"), primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id"), primary_key=True)


class Access(Base):
    __tablename__ = "accesses"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    resources: Mapped[list["Resource"]] = relationship("Resource", secondary="access_resources", back_populates="accesses")
    
    groups: Mapped[list["Group"]] = relationship("Group", secondary="group_accesses", back_populates="accesses")

