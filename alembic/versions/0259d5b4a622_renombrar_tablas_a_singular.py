"""renombrar_tablas_a_singular

Revision ID: 0259d5b4a622
Revises: dff1cbe6faf7
Create Date: 2017-05-13 11:55:48.066008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0259d5b4a622'
down_revision = 'dff1cbe6faf7'
branch_labels = None
depends_on = None


def upgrade():
    # Renombrar tablas a singular
    op.rename_table('productos', 'producto')
    op.rename_table('clientes', 'cliente')
    op.rename_table('pedidos', 'pedido')
    op.rename_table('pagos', 'pago')


def downgrade():
    # Y volvemos a plural
    op.rename_table('producto', 'productos')
    op.rename_table('cliente', 'clientes')
    op.rename_table('pedido', 'pedidos')
    op.rename_table('pago', 'pagos')
