import pytest

from pydantic import ValidationError

from src.dto.client_dto import ClientCreateDTO, ClientStatus
from src.dto.user_dto import UserCreateDTO


def test_client_dto_valid_nit_and_email():
    dto = ClientCreateDTO(
        company_id="00000000-0000-0000-0000-000000000000",
        email="contacto@acme.co",
        status=ClientStatus.ACTIVE,
    )


def test_client_dto_invalid_email():
    with pytest.raises(ValidationError):
        ClientCreateDTO(nit="800197268-4", business_name="Acme", email="not-an-email")


def test_user_dto_valid_lengths():
    dto = UserCreateDTO(
        name="John Doe",
        email="john@example.com",
        nickname="johnny",
        password="supersecret",
        company="Acme Inc",
    )
    assert dto.nickname == "johnny"


def test_user_dto_password_too_short():
    with pytest.raises(ValidationError):
        UserCreateDTO(name="J", email="a@b.co", password="short")


