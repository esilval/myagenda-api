from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import String, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class ClientStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    contact_name: Mapped[str] = mapped_column(String(255), nullable=True)
    company_id: Mapped[str] = mapped_column(String(36), ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=True, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)
    status: Mapped[ClientStatus] = mapped_column(SAEnum(ClientStatus, name="client_status"), nullable=False, default=ClientStatus.ACTIVE)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:  # pragma: no cover - developer helper
        return f"<Client id={self.id} nit={self.nit} status={self.status}>"

