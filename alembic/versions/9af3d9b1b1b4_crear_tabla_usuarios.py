"""crear_tabla_usuarios

Revision ID: 9af3d9b1b1b4
Revises: c64887e2090b
Create Date: 2017-05-04 03:37:29.923851

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9af3d9b1b1b4'
down_revision = 'c64887e2090b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('usuarios',
                    sa.Column('id_usuario', sa.Integer, primary_key=True, autoincrement=True),
                    sa.Column('email', sa.String(256), nullable=False),
                    sa.Column('credencial', sa.String(256), nullable=False),
                    sa.Column('fecha_registro', sa.DateTime, nullable=False),
                    sa.Column('nombres', sa.String(64), nullable=False),
                    sa.Column('apellidos', sa.String(64), nullable=False),
                    sa.Column('tipo_usuario', sa.SmallInteger, nullable=False))

    op.create_table('tipos_usuario',
                    sa.Column('id_tipo_usuario', sa.SmallInteger, primary_key=True, autoincrement=True),
                    sa.Column('desc_tipo_usuario', sa.String(32), nullable=False))

    # FK de Tipo de usuario
    op.create_foreign_key('tipo_usuario_fk', 'usuarios', 'tipos_usuario', ['tipo_usuario'], ['id_tipo_usuario'],
                          ondelete='CASCADE')


def downgrade():
    op.drop_table('usuarios')
    op.drop_table('tipos_usuario')
