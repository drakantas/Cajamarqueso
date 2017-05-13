"""crear_tipo_cliente

Revision ID: 21f492e55898
Revises: e27c17face2d
Create Date: 2017-05-04 01:38:12.564350

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '21f492e55898'
down_revision = 'e27c17face2d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('tipos_cliente',
                    sa.Column('id_tipo_cliente', sa.SmallInteger, primary_key=True, autoincrement=True),
                    sa.Column('desc_tipo_cliente', sa.String(32), nullable=False, unique=True))

    # Crear llave foránea para tipo_cliente en la tabla clientes
    op.create_foreign_key('tipo_cliente_fk', 'clientes', 'tipos_cliente', ['tipo_cliente'], ['id_tipo_cliente'],
                          ondelete='CASCADE')


def downgrade():
    # Droppear la llavea foránea de clientes
    op.drop_constraint('tipo_cliente_fk', 'clientes', type_='foreignkey')

    op.drop_table('tipos_cliente')
