from __future__ import annotations

from typing import Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.dao.client_dao import ClientDAO
from src.dto.client_dto import ClientCreateDTO, ClientDTO, ClientStatus
from src.models.client import Client
from src.dao.company_dao import CompanyDAO
from src.dao.user_client_dao import UserClientDAO
from src.models.user_client import UserClient


class ClientService:
    def __init__(self, db: Session):
        self.db = db
        self.dao = ClientDAO(db)

    def create(self, dto: ClientCreateDTO, *, current_user_id: str | None = None) -> ClientDTO:
        if dto.email and self.dao.get_by_email(dto.email):
            raise ValueError("EMAIL_TAKEN")
        if dto.phone and self.dao.get_by_phone(dto.phone):
            raise ValueError("PHONE_TAKEN")
        if not CompanyDAO(self.db).get_by_id(dto.company_id):
            raise ValueError("COMPANY_NOT_FOUND")
        client = Client(
            company_id=dto.company_id,
            contact_name=dto.contact_name,
            phone=dto.phone,
            email=dto.email,
            status=ClientStatus(dto.status.value),
        )
        client = self.dao.create(client)
        # Asociar el usuario creador si se proporcionó
        if current_user_id:
            uc_dao = UserClientDAO(self.db)
            existing = uc_dao.get_by_user_and_client(user_id=current_user_id, client_id=client.id)
            if not existing:
                uc_dao.create(UserClient(user_id=current_user_id, client_id=client.id))
        return self._to_dto(client)

    def update(self, client_id: str, dto: ClientCreateDTO) -> ClientDTO:
        client = self.dao.get_by_id(client_id)
        if not client:
            raise ValueError("NOT_FOUND")
        if dto.email and dto.email != client.email and self.dao.get_by_email(dto.email):
            raise ValueError("EMAIL_TAKEN")
        if dto.phone and dto.phone != client.phone and self.dao.get_by_phone(dto.phone):
            raise ValueError("PHONE_TAKEN")
        if dto.company_id and dto.company_id != client.company_id and not CompanyDAO(self.db).get_by_id(dto.company_id):
            raise ValueError("COMPANY_NOT_FOUND")

        client.contact_name = dto.contact_name
        client.company_id = dto.company_id
        client.phone = dto.phone
        client.email = dto.email
        client.status = ClientStatus(dto.status.value)
        client = self.dao.update(client)
        return self._to_dto(client)

    def deactivate(self, client_id: str) -> ClientDTO:
        client = self.dao.get_by_id(client_id)
        if not client:
            raise ValueError("NOT_FOUND")
        client.status = ClientStatus.INACTIVE
        client = self.dao.update(client)
        return self._to_dto(client)

    def delete(self, client_id: str) -> None:
        client = self.dao.get_by_id(client_id)
        if not client:
            raise ValueError("NOT_FOUND")
        self.dao.delete(client)

    def list_paginated(self, *, page: int = 1, size: int = 10, status: ClientStatus | None = None, text: str | None = None, current_user_id: str | None = None) -> Tuple[int, list[ClientDTO]]:
        stmt = self.dao.build_query(status=status, text=text, user_id=current_user_id)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()
        items = self.db.execute(stmt.limit(size).offset((page - 1) * size)).scalars().all()
        return total, [self._to_dto(c) for c in items]

    @staticmethod
    def _to_dto(c: Client) -> ClientDTO:
        return ClientDTO(
            id=c.id,
            company_id=c.company_id,
            contact_name=c.contact_name,
            phone=c.phone,
            email=c.email,
            status=ClientStatus(c.status.value),
            created_at=c.created_at,
            updated_at=c.updated_at,
        )


