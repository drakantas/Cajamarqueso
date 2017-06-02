"""crear_tabla_cliente

Revision ID: d9852688dadb
Revises: 87054484c002
Create Date: 2017-06-02 01:08:42.277191

"""
from alembic import op
import sqlalchemy as sa
from random import choice, randint


# revision identifiers, used by Alembic.
revision = 'd9852688dadb'
down_revision = '87054484c002'
branch_labels = None
depends_on = None


def upgrade():
    def populate_table(table):
        def generate_id(clients: list) -> int:
            id_ = randint(10000000, 99999999)
            if [x for x in clients if x['id_cliente'] == id_]:
                return generate_id(clients)
            return id_

        clients = list()
        possible_types = (0, 1)
        possible_names = (('Juan Perez', 'Pedro Perez', 'Juanita Espinoza', 'Jorge Sanchez del Rio', 'Miranda Reyes',
                           'Gabriel Tocado'), ('El Pescado de Cajamarca', 'Trucheria Cajamarca', 'La Sazón del Rey',
                                               'Miradando', 'Aoaque', 'Don Lito'))
        for t in range(0, 2):
            for c in range(0, 6):
                name = possible_names[t][c]
                client = {
                    'id_cliente': generate_id(clients),
                    'nombre_cliente': name,
                    'tipo_cliente': t + 1,
                    'email_cliente': name.lower().replace(' ', '_') + '@gmail.com',
                    'telefono_cliente': str(randint(100000000, 999999999))
                }

                clients.append(client)

        op.bulk_insert(table, clients)

    table = op.create_table('cliente',
                            sa.Column('id_cliente', sa.Integer, primary_key=True, autoincrement=False),
                            sa.Column('nombre_cliente', sa.String(256), nullable=False),
                            sa.Column('tipo_cliente', sa.SmallInteger, nullable=False),
                            sa.Column('email_cliente', sa.String(256), nullable=True),
                            sa.Column('telefono_cliente', sa.String(16), nullable=False))

    populate_table(table)


def downgrade():
    op.drop_table('cliente')
