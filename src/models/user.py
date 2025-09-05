from __future__ import annotations

import uuid
from datetime import datetime, timezone

from enum import Enum
from sqlalchemy import String, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    nickname: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # status: ACTIVE/INACTIVE
    # default ACTIVE
    # Using dedicated enum name for Postgres type
    class UserStatus(str, Enum):
        ACTIVE = "ACTIVE"
        INACTIVE = "INACTIVE"

    status: Mapped["User.UserStatus"] = mapped_column(
        SAEnum(UserStatus, name="user_status"), nullable=False, default=UserStatus.ACTIVE
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:  # pragma: no cover - developer helper
        return f"<User id={self.id} email={self.email}>"


