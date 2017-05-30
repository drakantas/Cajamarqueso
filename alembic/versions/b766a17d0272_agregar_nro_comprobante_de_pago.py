"""agregar_nro_comprobante_de_pago

Revision ID: b766a17d0272
Revises: 0476994dc286
Create Date: 2017-05-30 15:47:40.149297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b766a17d0272'
down_revision = '0476994dc286'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('pagos_pkey', 'pago', type_='primary')
    op.create_primary_key('pago_pkey', 'pago', ['pedido_id'])
    op.drop_column('pago', 'id_pago')
    op.add_column('pago', sa.Column('nro_comprobante', sa.String(24), nullable=False))


def downgrade():
    op.drop_constraint('pago_pkey', 'pago', type_='primary')
    op.add_column('pago', sa.Column('id_pago', sa.Integer, autoincrement=True))
    op.create_primary_key('pago_pkey', 'pago', ['id_pago'])
    op.drop_column('pago', 'nro_comprobante')
