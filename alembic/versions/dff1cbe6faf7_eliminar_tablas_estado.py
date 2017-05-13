"""eliminar_tablas_estado

Revision ID: dff1cbe6faf7
Revises: 9af3d9b1b1b4
Create Date: 2017-05-13 11:47:01.464800

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dff1cbe6faf7'
down_revision = '9af3d9b1b1b4'
branch_labels = None
depends_on = None


def upgrade():
    # Eliminar llaves foráneas de tablas relacionadas
    op.drop_constraint('estado_pedido_fk', 'pedidos', type_='foreignkey')
    op.drop_constraint('magnitud_producto_fk', 'productos', type_='foreignkey')
    op.drop_constraint('estado_pago_fk', 'pagos', type_='foreignkey')

    # Eliminar tablas
    op.drop_table('estados_pedido')
    op.drop_table('estados_pago')
    op.drop_table('magnitudes_producto')


def downgrade():
    # Reconstruir este desastre

    # Ver: crear_estados_pedido.py
    op.create_table('estados_pedido',
                    sa.Column('id_estado_pedido', sa.SmallInteger, primary_key=True, autoincrement=True),
                    sa.Column('desc_estado_pedido', sa.String(16), nullable=False))

    op.create_foreign_key('estado_pedido_fk', 'pedidos', 'estados_pedido', ['estado'],
                          ['id_estado_pedido'], ondelete='CASCADE')

    # Ver: crear_estados_pago.py
    op.create_table('estados_pago',
                    sa.Column('id_estado_pago', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('desc_estado_pago', sa.String(16), nullable=False))

    op.create_foreign_key('estado_pago_fk', 'pagos', 'estados_pago', ['estado'], ['id_estado_pago'], ondelete='CASCADE')

    # Ver: crear_magnitudes_producto.py
    op.create_table('magnitudes_producto',
                    sa.Column('id_magnitud_producto', sa.SmallInteger, primary_key=True, autoincrement=True),
                    sa.Column('desc_magnitud_producto', sa.String(16), nullable=False))

    op.create_foreign_key('magnitud_producto_fk', 'productos', 'magnitudes_producto', ['magnitud_producto'],
                          ['id_magnitud_producto'], ondelete='CASCADE')
