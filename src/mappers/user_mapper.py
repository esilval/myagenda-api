from __future__ import annotations

from src.dto.user_dto import UserDTO, UserCreateDTO
from src.models.user import User


def user_to_dto(entity: User) -> UserDTO:
    return UserDTO(
        id=entity.id,
        name=entity.name,
        email=entity.email,
        nickname=entity.nickname,
        password=entity.password,
        company=entity.company,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def dto_to_user(dto: UserCreateDTO) -> User:
    return User(
        name=dto.name,
        email=dto.email,
        nickname=dto.nickname,
        password=dto.password,
        company=dto.company,
    )

