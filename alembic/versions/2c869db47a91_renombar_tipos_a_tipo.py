"""Renombar_tipos_a_tipo

Revision ID: 2c869db47a91
Revises: c04248495f0e
Create Date: 2017-05-13 15:45:18.148489

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2c869db47a91'
down_revision = 'c04248495f0e'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('tipos_cliente', 'tipo_cliente')
    op.rename_table('tipos_usuario', 'tipo_usuario')


def downgrade():
    op.rename_table('tipo_cliente', 'tipos_cliente')
    op.rename_table('tipo_usuario', 'tipos_usuario')
