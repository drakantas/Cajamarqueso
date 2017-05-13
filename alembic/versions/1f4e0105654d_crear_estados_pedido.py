"""crear_estados_pedido

Revision ID: 1f4e0105654d
Revises: d687c3d29cfc
Create Date: 2017-05-04 03:08:55.121656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f4e0105654d'
down_revision = 'd687c3d29cfc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('estados_pedido',
                    sa.Column('id_estado_pedido', sa.SmallInteger, primary_key=True, autoincrement=True),
                    sa.Column('desc_estado_pedido', sa.String(16), nullable=False))

    # FK de estado de pedido para la tabla Pedidos
    op.create_foreign_key('estado_pedido_fk', 'pedidos', 'estados_pedido', ['estado'],
                          ['id_estado_pedido'], ondelete='CASCADE')


def downgrade():
    # Eliminar la FK de estado de pedido
    op.drop_constraint('estado_pedido_fk', 'pedidos', type_='foreignkey')

    op.drop_table('estados_pedido')
