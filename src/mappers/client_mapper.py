from __future__ import annotations

from src.dto.client_dto import ClientDTO, ClientCreateDTO, ClientStatus
from src.models.client import Client, ClientStatus as ModelStatus


def client_to_dto(entity: Client) -> ClientDTO:
    return ClientDTO(
        id=entity.id,
        company_id=entity.company_id,
        contact_name=entity.contact_name,
        phone=entity.phone,
        email=entity.email,
        status=ClientStatus(entity.status.value),
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def dto_to_client(dto: ClientCreateDTO) -> Client:
    return Client(
        company_id=dto.company_id,
        contact_name=dto.contact_name,
        phone=dto.phone,
        email=dto.email,
        status=ModelStatus(dto.status.value),
    )

