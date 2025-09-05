from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.company import Company


class CompanyDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, company_id: str) -> Optional[Company]:
        return self.db.get(Company, company_id)

    def get_by_nit(self, nit: str) -> Optional[Company]:
        stmt = select(Company).where(Company.nit == nit)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, company: Company) -> Company:
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def update(self, company: Company) -> Company:
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def delete(self, company: Company) -> None:
        self.db.delete(company)
        self.db.commit()

    def build_query(self, *, status: str | None = None, text: str | None = None):
        stmt = select(Company)
        if status:
            stmt = stmt.where(Company.status == status)
        if text:
            like = f"%{text.lower()}%"
            stmt = stmt.where((Company.business_name.ilike(like)) | (Company.city.ilike(like)) | (Company.nit.ilike(like)))
        return stmt.order_by(Company.created_at.desc())

    def get_by_ids(self, ids: Sequence[str]) -> list[Company]:
        if not ids:
            return []
        stmt = select(Company).where(Company.id.in_(list(ids)))
        return list(self.db.execute(stmt).scalars().all())


