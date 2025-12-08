from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from access_control_service.db.base import Base


class Conflict(Base):
    __tablename__ = "conflicts"
    
    group_id1: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True, index=True)
    group_id2: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True, index=True)
    
    group1: Mapped["Group"] = relationship(
        "Group",
        foreign_keys=[group_id1],
        back_populates="conflicts_as_group1"
    )
    group2: Mapped["Group"] = relationship(
        "Group",
        foreign_keys=[group_id2],
        back_populates="conflicts_as_group2"
    )
    

