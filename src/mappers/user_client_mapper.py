from __future__ import annotations

from src.dto.user_client_dto import UserClientDTO, UserClientCreateDTO
from src.models.user_client import UserClient


def user_client_to_dto(entity: UserClient) -> UserClientDTO:
    return UserClientDTO(
        id=entity.id,
        client_id=entity.client_id,
        user_id=entity.user_id,
        created_at=entity.created_at,
    )


def dto_to_user_client(dto: UserClientCreateDTO) -> UserClient:
    return UserClient(
        client_id=dto.client_id,
        user_id=dto.user_id,
    )

