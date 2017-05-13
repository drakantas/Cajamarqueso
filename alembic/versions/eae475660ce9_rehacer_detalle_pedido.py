"""rehacer_detalle_pedido

Revision ID: eae475660ce9
Revises: b8b05eafd1ad
Create Date: 2017-05-13 16:09:20.453020

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eae475660ce9'
down_revision = 'b8b05eafd1ad'
branch_labels = None
depends_on = None


def upgrade():
    # Eliminar tabla productos_pedidos
    op.drop_table('productos_pedidos')

    # Reconstruir productos_pedidos como detalle_pedido
    op.create_table('detalle_pedido', sa.Column('pedido_id', sa.Integer, primary_key=True),
                                      sa.Column('producto_id', sa.Integer, nullable=False),
                                      sa.Column('cantidad_producto', sa.SmallInteger, nullable=False, default=1))

    # Crear FKs
    op.create_foreign_key('pedido_id_fk', 'detalle_pedido', 'pedido', ['pedido_id'], ['id_pedido'],
                          ondelete='CASCADE')
    op.create_foreign_key('producto_id_fk', 'detalle_pedido', 'producto', ['producto_id'], ['id_producto'],
                          ondelete='CASCADE')


def downgrade():
    # Eliminar tabla
    op.drop_table('detalle_pedido')

    # Reconstruir productos_pedidos
    op.create_table('productos_pedidos',
                    sa.Column('id_productos_pedido', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('pedido_id', sa.Integer, nullable=False),
                    sa.Column('producto_id', sa.Integer, nullable=False),
                    sa.Column('cantidad_productos', sa.SmallInteger, nullable=False, default=1))

    # FKs de pedido y producto
    op.create_foreign_key('pedido_id_fk', 'productos_pedidos', 'pedido', ['pedido_id'],
                          ['id_pedido'], ondelete='CASCADE')
    op.create_foreign_key('producto_id_fk', 'productos_pedidos', 'producto', ['producto_id'],
                          ['id_producto'], ondelete='CASCADE')
