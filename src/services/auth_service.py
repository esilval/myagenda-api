from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.dao.user_dao import UserDAO
from src.models.user import User
from src.utils.jwt import create_access_token, decode_token
from src.utils.security import verify_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserDAO(db)

    def login(self, identifier: str, password: str) -> str:
        user = self._find_user(identifier)
        if not user or user.status != User.UserStatus.ACTIVE:
            raise ValueError("INVALID_CREDENTIALS")
        if not verify_password(password, user.password):
            raise ValueError("INVALID_CREDENTIALS")
        token = create_access_token({"sub": user.id})
        return token

    def authenticate(self, token: str) -> User:
        data = decode_token(token)
        user_id = data.get("sub")
        if not user_id:
            raise ValueError("INVALID_TOKEN")
        user = self.users.get_by_id(user_id)
        if not user or user.status != User.UserStatus.ACTIVE:
            raise ValueError("INVALID_TOKEN")
        return user

    def _find_user(self, identifier: str) -> User | None:
        # identifier can be email or nickname
        user = self.users.get_by_email(identifier)
        if user:
            return user
        return self.users.get_by_nickname(identifier)


