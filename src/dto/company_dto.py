from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator

from src.dto.client_dto import ClientStatus  # reuse enum style for status names
from src.utils.nit import validate_and_normalize_nit


class CompanyCreateDTO(BaseModel):
    nit: str
    business_name: str
    description: str | None = None
    address: str | None = None
    phone: str | None = None
    city: str | None = None
    status: ClientStatus = ClientStatus.ACTIVE

    @field_validator("nit")
    @classmethod
    def validate_nit(cls, v: str) -> str:
        return validate_and_normalize_nit(v)


class CompanyDTO(BaseModel):
    id: str
    nit: str
    business_name: str
    description: str | None = None
    address: str | None = None
    phone: str | None = None
    city: str | None = None
    status: ClientStatus
    created_at: datetime
    updated_at: datetime


