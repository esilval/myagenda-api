from __future__ import annotations

from sqlalchemy.orm import Session

from src.dao.user_dao import UserDAO
from src.dto.user_dto import UserCreateDTO, UserUpdateDTO, UserReadDTO
from src.models.user import User
from src.utils.security import hash_password


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.dao = UserDAO(db)

    def create_user(self, dto: UserCreateDTO) -> UserReadDTO:
        if self.dao.get_by_email(dto.email):
            raise ValueError("EMAIL_TAKEN")
        if dto.nickname and self.dao.get_by_nickname(dto.nickname):
            raise ValueError("NICKNAME_TAKEN")
        user = User(
            name=dto.name,
            email=dto.email,
            nickname=dto.nickname,
            password=hash_password(dto.password),
            company=dto.company,
        )
        user = self.dao.create(user)
        return self._to_read_dto(user)

    def update_user(self, user_id: str, dto: UserUpdateDTO) -> UserReadDTO:
        user = self.dao.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if dto.nickname:
            other = self.dao.get_by_nickname(dto.nickname)
            if other and other.id != user.id:
                raise ValueError("NICKNAME_TAKEN")
        if dto.name is not None:
            user.name = dto.name
        if dto.nickname is not None:
            user.nickname = dto.nickname
        if dto.password is not None:
            user.password = hash_password(dto.password)
        if dto.company is not None:
            user.company = dto.company
        user = self.dao.update(user)
        return self._to_read_dto(user)

    def set_active(self, user_id: str, active: bool) -> UserReadDTO:
        user = self.dao.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        user.status = User.UserStatus.ACTIVE if active else User.UserStatus.INACTIVE
        user = self.dao.update(user)
        return self._to_read_dto(user)

    @staticmethod
    def _to_read_dto(user: User) -> UserReadDTO:
        return UserReadDTO(
            id=user.id,
            name=user.name,
            email=user.email,
            nickname=user.nickname,
            company=user.company,
            status=user.status.value,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


