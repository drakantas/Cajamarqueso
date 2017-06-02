"""crear_tabla_producto

Revision ID: 39f326354ce7
Revises: d9852688dadb
Create Date: 2017-06-02 01:09:50.764234

"""
from alembic import op
import sqlalchemy as sa
from pathlib import Path
from os import listdir
from os.path import isfile
from random import choice, randint
from base64 import b64encode


# revision identifiers, used by Alembic.
revision = '39f326354ce7'
down_revision = 'd9852688dadb'
branch_labels = None
depends_on = None


def upgrade():

    def populate_table(table):
        resources_path = Path('./resources/assets/images/cheese')
        str_resources_path = str(resources_path.resolve())
        available_images = [str(resources_path.joinpath(i).resolve()) for i in listdir(str_resources_path)
                            if isfile(str(resources_path.joinpath(i).resolve()))]
        possible_names = ('Queso Suizo', 'Queso Cheddar', 'Queso Mozzarella', 'Queso Fresco', 'Queso Añejado',
                          'Queso Cajamarquino')
        possible_varieties = ('1kg', '2kg', '3kg', '4kg', '5kg', '6kg')
        possible_prices = (27.50, 14.50, 29.70, 38.90, 40.50)
        possible_packages = ('Plástico', 'Cartón', 'Vidrio')
        possible_units = (1,)
        products = list()

        for p in possible_names:
            product = {
                'nombre_producto': p,
                'variedad_producto': choice(possible_varieties),
                'presentacion_producto': choice(possible_packages),
                'magnitud_producto': choice(possible_units),
                'stock': randint(50, 400),
                'precio': choice(possible_prices),
                'imagen_producto': None
            }
            with open(choice(available_images), 'rb') as f:
                product['imagen_producto'] = bytearray(b64encode(f.read()))

            products.append(product)

        op.bulk_insert(table, products)

    table = op.create_table('producto',
                            sa.Column('id_producto', sa.Integer, primary_key=True, autoincrement=True),
                            sa.Column('nombre_producto', sa.String(128), nullable=False, unique=True),
                            sa.Column('variedad_producto', sa.String(64), nullable=False),
                            sa.Column('presentacion_producto', sa.String(32), nullable=False),
                            sa.Column('magnitud_producto', sa.SmallInteger, nullable=False),
                            sa.Column('stock', sa.SmallInteger, nullable=False),
                            sa.Column('precio', sa.Numeric, nullable=False),
                            sa.Column('imagen_producto', sa.Binary, nullable=False))

    populate_table(table)


def downgrade():
    op.drop_table('producto')
