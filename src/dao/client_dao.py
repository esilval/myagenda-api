from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from src.models.client import Client, ClientStatus
from src.models.user_client import UserClient


class ClientDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, client_id: str) -> Optional[Client]:
        return self.db.get(Client, client_id)

    def get_by_email(self, email: str) -> Optional[Client]:
        stmt = select(Client).where(Client.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_phone(self, phone: str) -> Optional[Client]:
        stmt = select(Client).where(Client.phone == phone)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, client: Client) -> Client:
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def update(self, client: Client) -> Client:
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return client

    def delete(self, client: Client) -> None:
        self.db.delete(client)
        self.db.commit()

    def build_query(
        self,
        *,
        status: ClientStatus | None = None,
        text: str | None = None,
        user_id: str | None = None,
    ) -> Select:
        stmt = select(Client)
        if user_id:
            stmt = stmt.join(UserClient, UserClient.client_id == Client.id).where(UserClient.user_id == user_id)
        if status is not None:
            stmt = stmt.where(Client.status == status)
        if text:
            like = f"%{text.lower()}%"
            stmt = stmt.where(
                (Client.contact_name.ilike(like)) | (Client.phone.ilike(like)) | (Client.email.ilike(like))
            )
        return stmt.order_by(Client.created_at.desc())


