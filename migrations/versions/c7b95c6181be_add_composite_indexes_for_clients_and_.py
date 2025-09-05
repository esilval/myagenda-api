"""add composite indexes for clients and companies

Revision ID: c7b95c6181be
Revises: 66b42469cfac
Create Date: 2025-09-05 11:08:16.201374

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7b95c6181be'
down_revision: Union[str, None] = '66b42469cfac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Clients composite indexes: (company_id, status), (status, created_at), (company_id, created_at)
    op.create_index("ix_clients_company_status", "clients", ["company_id", "status"], unique=False)
    op.create_index("ix_clients_status_created", "clients", ["status", "created_at"], unique=False)
    op.create_index("ix_clients_company_created", "clients", ["company_id", "created_at"], unique=False)

    # Companies composite indexes: (status, city), (business_name, city)
    op.create_index("ix_companies_status_city", "companies", ["status", "city"], unique=False)
    op.create_index("ix_companies_name_city", "companies", ["business_name", "city"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_companies_name_city", table_name="companies")
    op.drop_index("ix_companies_status_city", table_name="companies")
    op.drop_index("ix_clients_company_created", table_name="clients")
    op.drop_index("ix_clients_status_created", table_name="clients")
    op.drop_index("ix_clients_company_status", table_name="clients")
