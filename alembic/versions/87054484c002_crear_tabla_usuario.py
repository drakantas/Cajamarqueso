"""crear_tabla_usuario

Revision ID: 87054484c002
Revises: 
Create Date: 2017-06-02 01:07:34.141465

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87054484c002'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('usuario',
                    sa.Column('id_usuario', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('email', sa.String(256), nullable=False),
                    sa.Column('credencial', sa.String(256), nullable=False),
                    sa.Column('fecha_registro', sa.DateTime, nullable=False),
                    sa.Column('nombres', sa.String(64), nullable=False),
                    sa.Column('apellidos', sa.String(64), nullable=False),
                    sa.Column('tipo_usuario', sa.SmallInteger, nullable=False))


def downgrade():
    op.drop_table('usuario')
