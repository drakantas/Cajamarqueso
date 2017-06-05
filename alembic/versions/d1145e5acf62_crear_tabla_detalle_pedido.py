"""crear_tabla_detalle_pedido

Revision ID: d1145e5acf62
Revises: 7f843032b028
Create Date: 2017-06-02 01:23:02.710630

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1145e5acf62'
down_revision = '7f843032b028'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('detalle_pedido',
                    sa.Column('pedido_cod', sa.String(32), primary_key=True),
                    sa.Column('producto_id', sa.Integer, primary_key=True),
                    sa.Column('cantidad', sa.SmallInteger, nullable=False))

    op.create_foreign_key('pedido_cod_fk', 'detalle_pedido', 'pedido', ['pedido_cod'], ['cod_pedido'],
                          ondelete='CASCADE', onupdate='CASCADE')
    op.create_foreign_key('producto_id_fk', 'detalle_pedido', 'producto', ['producto_id'], ['id_producto'],
                          ondelete='CASCADE', onupdate='CASCADE')


def downgrade():
    op.drop_table('detalle_pedido')
