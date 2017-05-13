"""crear_tabla_pedidos

Revision ID: 5cbc635100f7
Revises: e1f64f52475e
Create Date: 2017-05-04 02:37:04.425093

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5cbc635100f7'
down_revision = 'e1f64f52475e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('pedidos',
                    sa.Column('id_pedido', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('cliente_id', sa.Integer, nullable=False),
                    sa.Column('fecha_realizado', sa.DateTime, nullable=False),
                    sa.Column('estado', sa.SmallInteger, nullable=False))

    # FK de Cliente al cual pertenece el pedido
    op.create_foreign_key('cliente_id_fk', 'pedidos', 'clientes', ['cliente_id'],
                          ['id_cliente'], ondelete='CASCADE')


def downgrade():
    op.drop_table('pedidos')
