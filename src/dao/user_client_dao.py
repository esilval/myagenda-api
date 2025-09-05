from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.user_client import UserClient


class UserClientDAO:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_and_client(self, *, user_id: str, client_id: str) -> Optional[UserClient]:
        stmt = select(UserClient).where(UserClient.user_id == user_id, UserClient.client_id == client_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, entity: UserClient) -> UserClient:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity


