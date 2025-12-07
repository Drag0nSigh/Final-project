from __future__ import annotations

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from access_control_service.db.base import Base


class GroupAccess(Base):
    """Association таблица между Group и Access"""
    __tablename__ = "group_accesses"
    
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    access_id: Mapped[int] = mapped_column(ForeignKey("accesses.id"), primary_key=True)


class Group(Base):
    __tablename__ = "groups"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    
    accesses: Mapped[list["Access"]] = relationship("Access", secondary="group_accesses", back_populates="groups")
    
    conflicts_as_group1: Mapped[list["Conflict"]] = relationship(
        "Conflict",
        foreign_keys=["Conflict.group_id1"],
        back_populates="group1"
    )
    conflicts_as_group2: Mapped[list["Conflict"]] = relationship(
        "Conflict",
        foreign_keys=["Conflict.group_id2"],
        back_populates="group2"
    )

