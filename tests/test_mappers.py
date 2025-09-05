from src.dto.client_dto import ClientCreateDTO, ClientStatus
from src.mappers.client_mapper import dto_to_client


def test_mapper_company_id_passthrough():
    dto = ClientCreateDTO(company_id="00000000-0000-0000-0000-000000000000", status=ClientStatus.ACTIVE)
    entity = dto_to_client(dto)
    assert entity.company_id == "00000000-0000-0000-0000-000000000000"


