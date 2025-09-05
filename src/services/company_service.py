from __future__ import annotations

from typing import Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.dao.company_dao import CompanyDAO
from src.dto.company_dto import CompanyCreateDTO, CompanyDTO, ClientStatus
from src.models.company import Company, CompanyStatus


class CompanyService:
    def __init__(self, db: Session):
        self.db = db
        self.dao = CompanyDAO(db)

    def create(self, dto: CompanyCreateDTO) -> CompanyDTO:
        if self.dao.get_by_nit(dto.nit):
            raise ValueError("NIT_TAKEN")
        company = Company(
            nit=dto.nit,
            business_name=dto.business_name,
            description=dto.description,
            address=dto.address,
            phone=dto.phone,
            city=dto.city,
            status=CompanyStatus(dto.status.value),
        )
        company = self.dao.create(company)
        return self._to_dto(company)

    def get(self, company_id: str) -> CompanyDTO:
        c = self.dao.get_by_id(company_id)
        if not c:
            raise ValueError("NOT_FOUND")
        return self._to_dto(c)

    def update(self, company_id: str, dto: CompanyCreateDTO) -> CompanyDTO:
        c = self.dao.get_by_id(company_id)
        if not c:
            raise ValueError("NOT_FOUND")
        if dto.nit != c.nit and self.dao.get_by_nit(dto.nit):
            raise ValueError("NIT_TAKEN")
        c.nit = dto.nit
        c.business_name = dto.business_name
        c.description = dto.description
        c.address = dto.address
        c.phone = dto.phone
        c.city = dto.city
        c.status = CompanyStatus(dto.status.value)
        c = self.dao.update(c)
        return self._to_dto(c)

    def delete(self, company_id: str) -> None:
        c = self.dao.get_by_id(company_id)
        if not c:
            raise ValueError("NOT_FOUND")
        self.dao.delete(c)

    def list_paginated(self, *, page: int = 1, size: int = 10, status: str | None = None, text: str | None = None) -> Tuple[int, list[CompanyDTO]]:
        stmt = self.dao.build_query(status=status, text=text)
        total = self.db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()
        items = self.db.execute(stmt.limit(size).offset((page - 1) * size)).scalars().all()
        return total, [self._to_dto(i) for i in items]

    @staticmethod
    def _to_dto(c: Company) -> CompanyDTO:
        return CompanyDTO(
            id=c.id,
            nit=c.nit,
            business_name=c.business_name,
            description=c.description,
            address=c.address,
            phone=c.phone,
            city=c.city,
            status=ClientStatus(c.status.value),
            created_at=c.created_at,
            updated_at=c.updated_at,
        )


