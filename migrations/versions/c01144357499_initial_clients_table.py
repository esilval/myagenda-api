"""initial clients table

Revision ID: c01144357499
Revises: 
Create Date: 2025-09-04 17:02:34.021485

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c01144357499'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    client_status = postgresql.ENUM('ACTIVE', 'INACTIVE', name='client_status', create_type=True)
    client_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'clients',
        sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
        sa.Column('nit', sa.String(length=9), nullable=False),
        sa.Column('business_name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.String(length=100), nullable=True),
        sa.Column('contact_name', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('status', postgresql.ENUM(name='client_status', create_type=False), nullable=False, server_default='ACTIVE'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    op.create_index('ix_clients_nit', 'clients', ['nit'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_clients_nit', table_name='clients')
    op.drop_table('clients')

    client_status = sa.Enum('ACTIVE', 'INACTIVE', name='client_status')
    client_status.drop(op.get_bind(), checkfirst=True)
