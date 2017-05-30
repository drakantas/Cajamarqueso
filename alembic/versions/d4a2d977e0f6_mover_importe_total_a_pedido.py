"""mover_importe_total_a_pedido

Revision ID: d4a2d977e0f6
Revises: b766a17d0272
Create Date: 2017-05-30 16:17:08.920039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4a2d977e0f6'
down_revision = 'b766a17d0272'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('pago', 'importe_pagado')
    op.add_column('pedido', sa.Column('importe_pagado', sa.Numeric, nullable=False))


def downgrade():
    op.drop_column('pedido', 'importe_pagado')
    op.add_column('pago', sa.Column('importe_pagado', sa.Numeric, nullable=False))
