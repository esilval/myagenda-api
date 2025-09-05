"""enable pg_trgm and add trigram/functional indexes

Revision ID: 7ccab2225c10
Revises: c7b95c6181be
Create Date: 2025-09-05 11:10:59.647764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ccab2225c10'
down_revision: Union[str, None] = 'c7b95c6181be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable extension
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Trigram indexes for case-insensitive search on text columns
    op.execute("CREATE INDEX IF NOT EXISTS ix_clients_contact_name_trgm ON clients USING gin (contact_name gin_trgm_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_clients_email_trgm ON clients USING gin (email gin_trgm_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_clients_phone_trgm ON clients USING gin (phone gin_trgm_ops)")

    op.execute("CREATE INDEX IF NOT EXISTS ix_companies_name_trgm ON companies USING gin (business_name gin_trgm_ops)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_companies_city_trgm ON companies USING gin (city gin_trgm_ops)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_companies_city_trgm")
    op.execute("DROP INDEX IF EXISTS ix_companies_name_trgm")
    op.execute("DROP INDEX IF EXISTS ix_clients_phone_trgm")
    op.execute("DROP INDEX IF EXISTS ix_clients_email_trgm")
    op.execute("DROP INDEX IF EXISTS ix_clients_contact_name_trgm")
