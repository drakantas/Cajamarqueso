"""crear_estados_pago

Revision ID: c64887e2090b
Revises: e00a0533a0b2
Create Date: 2017-05-04 03:19:06.563253

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c64887e2090b'
down_revision = 'e00a0533a0b2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('estados_pago',
                    sa.Column('id_estado_pago', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('desc_estado_pago', sa.String(16), nullable=False))

    # FK de pago, referencia a estado de pago
    op.create_foreign_key('estado_pago_fk', 'pagos', 'estados_pago', ['estado'], ['id_estado_pago'], ondelete='CASCADE')


def downgrade():
    op.drop_constraint('estado_pago_fk', 'pagos', type_='foreignkey')
    op.drop_table('estados_pago')
