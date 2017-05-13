"""rehacer_fks_de_tipo

Revision ID: b8b05eafd1ad
Revises: 2c869db47a91
Create Date: 2017-05-13 15:49:03.826433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8b05eafd1ad'
down_revision = '2c869db47a91'
branch_labels = None
depends_on = None


def upgrade():
    # Renombrar tabla usuarios a usuario
    op.rename_table('usuarios', 'usuario')

    # Droppear las FKs
    op.drop_constraint('tipo_cliente_fk', 'cliente', type_='foreignkey')
    op.drop_constraint('tipo_usuario_fk', 'usuario', type_='foreignkey')

    # Modificar columna tipo, podrá ser núlo y se agrega _id al final del nombre de columna
    op.alter_column('cliente', 'tipo_cliente', nullable=True, new_column_name='tipo_cliente_id')
    op.alter_column('usuario', 'tipo_usuario', nullable=True, new_column_name='tipo_usuario_id')

    # Rehacer las FKs
    op.create_foreign_key('tipo_cliente_id_fk', 'cliente', 'tipo_cliente', ['tipo_cliente_id'], ['id_tipo_cliente'],
                          ondelete='SET NULL')
    op.create_foreign_key('tipo_usuario_id_fk', 'usuario', 'tipo_usuario', ['tipo_usuario_id'], ['id_tipo_usuario'],
                          ondelete='SET NULL')


def downgrade():
    # ...
    op.rename_table('usuario', 'usuarios')

    # Eliminar las FKs
    op.drop_constraint('tipo_cliente_id_fk', 'cliente', type_='foreignkey')
    op.drop_constraint('tipo_usuario_id_fk', 'usuarios', type_='foreignkey')

    # Modificar columnas, regresar al estado anterior
    op.alter_column('cliente', 'tipo_cliente_id', nullable=False, new_column_name='tipo_cliente')
    op.alter_column('usuarios', 'tipo_usuario_id', nullable=False, new_column_name='tipo_usuario')

    # Crear las FKs
    op.create_foreign_key('tipo_cliente_fk', 'cliente', 'tipo_cliente', ['tipo_cliente'], ['id_tipo_cliente'],
                          ondelete='CASCADE')
    op.create_foreign_key('tipo_usuario_fk', 'usuarios', 'tipo_usuario', ['tipo_usuario'], ['id_tipo_usuario'],
                          ondelete='CASCADE')
