"""crear_tabla_productos

Revision ID: 4bf8bb816f0e
Revises: 21f492e55898
Create Date: 2017-05-04 02:01:17.037206

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4bf8bb816f0e'
down_revision = '21f492e55898'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('productos',
                    sa.Column('id_producto', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('nombre_producto', sa.String(128), nullable=False, unique=True),
                    sa.Column('variedad_producto', sa.String(64), nullable=False),
                    sa.Column('presentacion_producto', sa.String(32), nullable=False),
                    sa.Column('magnitud_producto', sa.SmallInteger, nullable=False),
                    sa.Column('stock', sa.SmallInteger, nullable=False),
                    sa.Column('imagen_producto', sa.Binary, nullable=False))


def downgrade():
    op.drop_table('productos')
