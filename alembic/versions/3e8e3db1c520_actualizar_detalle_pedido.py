"""actualizar_detalle_pedido

Revision ID: 3e8e3db1c520
Revises: eae475660ce9
Create Date: 2017-05-15 14:41:40.129177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3e8e3db1c520'
down_revision = 'eae475660ce9'
branch_labels = None
depends_on = None


def upgrade():
    # Eliminar FKs
    op.drop_constraint('pedido_id_fk', 'detalle_pedido', type_='foreignkey')
    op.drop_constraint('producto_id_fk', 'detalle_pedido', type_='foreignkey')

    # Eliminar tabla
    op.drop_table('detalle_pedido')

    # Reconstruir tabla
    op.create_table('detalle_pedido', sa.Column('id_detalle_pedido', sa.Integer, primary_key=True, autoincrement=True),
                                      sa.Column('pedido_id', sa.Integer, nullable=False),
                                      sa.Column('producto_id', sa.Integer, nullable=False),
                                      sa.Column('cantidad', sa.SmallInteger, nullable=False, default=1))

    # Reconstruir FKs
    op.create_foreign_key('pedido_id_fk', 'detalle_pedido', 'pedido', ['pedido_id'], ['id_pedido'],
                          ondelete='CASCADE')
    op.create_foreign_key('producto_id_fk', 'detalle_pedido', 'producto', ['producto_id'], ['id_producto'],
                          ondelete='CASCADE')


def downgrade():
    # Eliminar FKs
    op.drop_constraint('pedido_id_fk', 'detalle_pedido', type_='foreignkey')
    op.drop_constraint('producto_id_fk', 'detalle_pedido', type_='foreignkey')

    # Eliminar tabla
    op.drop_table('detalle_pedido')

    # ...
    op.create_table('detalle_pedido', sa.Column('pedido_id', sa.Integer, primary_key=True),
                    sa.Column('producto_id', sa.Integer, nullable=False),
                    sa.Column('cantidad_producto', sa.SmallInteger, nullable=False, default=1))

    # Crear FKs
    op.create_foreign_key('pedido_id_fk', 'detalle_pedido', 'pedido', ['pedido_id'], ['id_pedido'],
                          ondelete='CASCADE')
    op.create_foreign_key('producto_id_fk', 'detalle_pedido', 'producto', ['producto_id'], ['id_producto'],
                          ondelete='CASCADE')
