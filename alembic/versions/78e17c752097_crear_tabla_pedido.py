"""crear_tabla_pedido

Revision ID: 78e17c752097
Revises: 39f326354ce7
Create Date: 2017-06-02 01:12:07.453171

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78e17c752097'
down_revision = '39f326354ce7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('pedido',
                    sa.Column('cod_pedido', sa.String(32), primary_key=True),
                    sa.Column('cliente_id', sa.Integer, nullable=False),
                    sa.Column('estado', sa.SmallInteger, nullable=False),
                    sa.Column('entrega', sa.SmallInteger, nullable=False),
                    sa.Column('fecha_realizado', sa.DateTime, nullable=False),
                    sa.Column('importe_pagado', sa.Numeric, nullable=False))

    op.create_foreign_key('cliente_id_fk', 'pedido', 'cliente', ['cliente_id'], ['id_cliente'], ondelete='CASCADE')


def downgrade():
    op.drop_table('pedido')
