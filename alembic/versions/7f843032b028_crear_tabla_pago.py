"""crear_tabla_pago

Revision ID: 7f843032b028
Revises: 78e17c752097
Create Date: 2017-06-02 01:15:30.198282

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f843032b028'
down_revision = '78e17c752097'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('pago',
                    sa.Column('pedido_cod', sa.String(32), primary_key=True),
                    sa.Column('fecha_realizado', sa.DateTime, nullable=False),
                    sa.Column('cod_comprobante', sa.String(24), nullable=False, unique=True))

    op.create_foreign_key('pedido_cod_fk', 'pago', 'pedido', ['pedido_cod'], ['cod_pedido'], ondelete='CASCADE')


def downgrade():
    op.drop_table('pago')
