"""Eliminar estado de pago.

Revision ID: 0476994dc286
Revises: 068525608202
Create Date: 2017-05-26 14:38:05.845821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0476994dc286'
down_revision = '068525608202'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('pago', 'estado')


def downgrade():
    op.add_column('pago', sa.Column('estado', sa.SmallInteger, nullable=False))
