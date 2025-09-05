from __future__ import annotations

from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr


class ClientStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class ClientCreateDTO(BaseModel):
    contact_name: str | None = None
    company_id: str
    phone: str | None = None
    email: EmailStr | None = None
    status: ClientStatus = ClientStatus.ACTIVE


class ClientDTO(BaseModel):
    id: str
    company_id: str
    contact_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    status: ClientStatus
    created_at: datetime
    updated_at: datetime

