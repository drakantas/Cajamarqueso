"""crear_tabla_pagos

Revision ID: e00a0533a0b2
Revises: 1f4e0105654d
Create Date: 2017-05-04 03:12:48.717828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e00a0533a0b2'
down_revision = '1f4e0105654d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('pagos',
                    sa.Column('id_pago', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('pedido_id', sa.Integer, nullable=False),
                    sa.Column('importe_pagado', sa.Numeric, nullable=False),
                    sa.Column('fecha_realizado', sa.DateTime, nullable=False),
                    sa.Column('estado', sa.SmallInteger, nullable=False))

    # FK de pedido
    op.create_foreign_key('pedido_id_fk', 'pagos', 'pedidos', ['pedido_id'], ['id_pedido'], ondelete='CASCADE')


def downgrade():
    op.drop_table('pagos')
