"""crear_productos_por_pedido

Revision ID: d687c3d29cfc
Revises: 5cbc635100f7
Create Date: 2017-05-04 02:54:14.968160

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd687c3d29cfc'
down_revision = '5cbc635100f7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('productos_pedidos',
                    sa.Column('id_productos_pedido', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('pedido_id', sa.Integer, nullable=False),
                    sa.Column('producto_id', sa.Integer, nullable=False),
                    sa.Column('cantidad_productos', sa.SmallInteger, nullable=False, default=1))

    # FKs de pedido y producto
    op.create_foreign_key('pedido_id_fk', 'productos_pedidos', 'pedidos', ['pedido_id'],
                          ['id_pedido'], ondelete='CASCADE')
    op.create_foreign_key('producto_id_fk', 'productos_pedidos', 'productos', ['producto_id'],
                          ['id_producto'], ondelete='CASCADE')


def downgrade():
    op.drop_table('productos_pedidos')
