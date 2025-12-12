from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from user_service.db.base import Base


class UserPermission(Base):
    __tablename__ = "user_permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    permission_type: Mapped[str] = mapped_column(String(20), nullable=False)
    item_id: Mapped[int] = mapped_column(nullable=False)
    item_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    request_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="permissions")

    __table_args__ = (
        UniqueConstraint('user_id', 'permission_type', 'item_id', name='unique_user_permission'),
    )
