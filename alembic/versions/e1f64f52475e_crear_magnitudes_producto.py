"""crear_magnitudes_producto

Revision ID: e1f64f52475e
Revises: 4bf8bb816f0e
Create Date: 2017-05-04 02:09:00.397374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1f64f52475e'
down_revision = '4bf8bb816f0e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('magnitudes_producto',
                    sa.Column('id_magnitud_producto', sa.SmallInteger, primary_key=True, autoincrement=True),
                    sa.Column('desc_magnitud_producto', sa.String(16), nullable=False))

    # Crear FK de magnitud de producto
    op.create_foreign_key('magnitud_producto_fk', 'productos', 'magnitudes_producto', ['magnitud_producto'],
                          ['id_magnitud_producto'], ondelete='CASCADE')


def downgrade():
    # Droppear la FK de productos
    op.drop_constraint('magnitud_producto_fk', 'productos', type_='foreignkey')

    op.drop_table('magnitudes_producto')
