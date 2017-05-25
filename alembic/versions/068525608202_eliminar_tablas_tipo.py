"""Eliminar tablas tipo

Revision ID: 068525608202
Revises: 3e8e3db1c520
Create Date: 2017-05-25 00:37:07.061786

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '068525608202'
down_revision = '3e8e3db1c520'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('tipo_cliente_id_fk', 'cliente', type_='foreignkey')
    op.drop_constraint('tipo_usuario_id_fk', 'usuario', type_='foreignkey')

    op.drop_table('tipo_cliente')
    op.drop_table('tipo_usuario')


def downgrade():
    op.create_table('tipo_cliente',
                    sa.Column('id_tipo_cliente', sa.SmallInteger, primary_key=True, autoincrement=True),
                    sa.Column('desc_tipo_cliente', sa.String(32), nullable=False, unique=True))
    op.create_table('tipo_usuario',
                    sa.Column('id_tipo_usuario', sa.SmallInteger, primary_key=True, autoincrement=True),
                    sa.Column('desc_tipo_usuario', sa.String(32), nullable=False))

    op.create_foreign_key('tipo_cliente_id_fk', 'cliente', 'tipo_cliente', ['tipo_cliente_id'], ['id_tipo_cliente'],
                          ondelete='SET NULL')
    op.create_foreign_key('tipo_usuario_id_fk', 'usuario', 'tipo_usuario', ['tipo_usuario_id'], ['id_tipo_usuario'],
                          ondelete='SET NULL')
