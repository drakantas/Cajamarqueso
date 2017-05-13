"""columna_costos_en_producto

Revision ID: c04248495f0e
Revises: 0259d5b4a622
Create Date: 2017-05-13 15:36:08.386568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c04248495f0e'
down_revision = '0259d5b4a622'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('producto', sa.Column('precio', sa.Numeric, nullable=False))


def downgrade():
    op.drop_column('producto', 'precio')
