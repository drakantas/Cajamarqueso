"""crear_tabla_clientes

Revision ID: e27c17face2d
Revises: 
Create Date: 2017-05-04 01:07:34.649107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e27c17face2d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('clientes',
                    sa.Column('id_cliente', sa.Integer, primary_key=True, autoincrement=False),
                    sa.Column('tipo_cliente', sa.SmallInteger, nullable=False),
                    sa.Column('nombre_cliente', sa.String(256), nullable=False),
                    sa.Column('email_cliente', sa.String(256), nullable=True),
                    sa.Column('telefono_cliente', sa.String(16), nullable=False))


def downgrade():
    op.drop_table('clientes')
