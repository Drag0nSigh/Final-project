from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint

from access_control_service.db.base import Base


class Conflict(Base):
    """Таблица конфликтов между группами прав"""
    __tablename__ = "conflicts"
    
    group_id1 = Column(Integer, ForeignKey("groups.id"), primary_key=True, index=True)
    group_id2 = Column(Integer, ForeignKey("groups.id"), primary_key=True, index=True)
    
    # Relationships для удобного доступа к группам
    group1 = relationship(
        "Group",
        foreign_keys=[group_id1],
        back_populates="conflicts_as_group1"
    )
    group2 = relationship(
        "Group",
        foreign_keys=[group_id2],
        back_populates="conflicts_as_group2"
    )
    
    # Composite Primary Key автоматически создается через primary_key=True на обеих колонках

