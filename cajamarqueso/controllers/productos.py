from typing import Union
from base64 import b64encode
from aiohttp.web import json_response, HTTPNotFound
from aiohttp_jinja2 import template
from decimal import Decimal, InvalidOperation

from ..abc import Controller
from ..decorators import get_usuario, usuario_debe_estar_conectado, admin_y_encargado_produccion

try:
    import ujson as json
except ImportError:
    import json

Controllers = ('ListarProductos', 'BuscarProductos', 'RegistrarProducto', 'ModificarProducto')


class RegistrarProducto(Controller):
    @template('productos/registrar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_produccion
    async def get(self, request, usuario):
        return {'usuario': usuario}

    @template('productos/registrar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_produccion
    async def post(self, request, usuario):
        try:
            data = await request.post()
        except ValueError:
            return {'error': 'El archivo que intenta subir es demasiado pesado.',
                    'usuario': usuario}

        # lol = b64encode(data['imagen_producto'].file.read()).decode('utf-8')
        validated_data = await self.validate(data)

        if isinstance(validated_data, str):
            alert = {'error': validated_data}
        else:
            create = await self.create(validated_data)

            if create:
                alert = {'success': 'Se ha registrado el producto exitosamente.'}
            else:
                alert = {'error': 'No se pudo registrar el producto. Por favor, inténtelo de nuevo más tarde.'}

        return {**alert,
                'usuario': usuario}

    async def validate(self, data) -> Union[str, dict]:
        nombre = data['nombre_producto'].strip()
        peso_neto = data['peso_neto_producto'].strip()
        presentacion = data['presentacion_producto'].strip()
        stock = data['stock_producto'].strip()
        precio = data['precio_producto'].strip()
        imagen = data['imagen_producto']

        if nombre == '' or peso_neto == '' or presentacion == '' or stock == '' or precio == '' or imagen == b'':
            return 'Debes de llenar todos los campos del formulario, y seleccionar una imagen.'

        if not 8 <= len(nombre) <= 32:
            return 'El nombre del producto debe de contener entre 8 y 128 caracteres.'
        elif not 3 <= len(peso_neto) <= 8:
            return 'El peso neto del producto debe de contener entre 3 y 8 caracteres.'
        elif not 5 <= len(presentacion) <= 16:
            return 'La presentación del producto debe de contener entre 5 y 16 caracteres.'

        try:
            stock = int(stock)
        except ValueError:
            return 'El stock debe de ser un número entero.'

        try:
            precio = Decimal(precio)
        except InvalidOperation:
            return 'El precio debe de ser un número entero o decimal.'

        if stock < 0:
            return 'El stock no puede ser menor que 0.'
        elif precio <= Decimal(0):
            return 'El precio no puede ser menor o igual que 0.'

        if imagen.headers['Content-Type'] not in ('image/png', 'image/jpeg'):
            return 'El formato de la imagen no es correcto. Solo se soporta imágenes .png y .jpeg'

        if not (await self.verify(nombre, peso_neto)):
            return 'Ya existe un producto con el mismo nombre y peso neto.'

        return {
            'nombre': nombre,
            'peso_neto': peso_neto,
            'presentacion': presentacion,
            'stock': stock,
            'precio': precio,
            'imagen': bytearray(b64encode(imagen.file.read()))
        }

    async def create(self, data: dict):
        producto_model = self.app.mvc.models['producto']

        return await producto_model.create(data)

    async def verify(self, nombre: str, peso_neto: str) -> str:
        producto_model = self.app.mvc.models['producto']

        return await producto_model.verify(nombre, peso_neto)


class ModificarProducto(Controller):
    @template('productos/registrar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_produccion
    async def get(self, request, usuario):
        producto = await self.producto(int(request.match_info['id_producto']))

        if not producto:
            raise HTTPNotFound

        return {'usuario': usuario,
                'producto': producto}

    @template('productos/registrar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_produccion
    async def post(self, request, usuario):
        producto = await self.producto(int(request.match_info['id_producto']))

        if not producto:
            raise HTTPNotFound

        try:
            data = await request.post()
        except ValueError:
            return {'error': 'El archivo que intenta subir es demasiado pesado.',
                    'usuario': usuario,
                    'producto': producto}

        validated_data = await self.validate(data, producto['id_producto'])

        if isinstance(validated_data, str):
            alert = {'error': validated_data}
        else:
            update = await self.update(validated_data, producto['id_producto'])
            if not update:
                alert = {'error': 'No se pudo actualizar el producto. Por favor, inténtelo más tarde.'}
            else:
                alert = {'success': 'Se actualizó el producto exitosamente.'}

        return {**alert,
                'usuario': usuario,
                'producto': (await self.producto(int(request.match_info['id_producto'])))}

    async def validate(self, data, id_producto: int) -> Union[str, dict]:
        nombre = data['nombre_producto'].strip()
        peso_neto = data['peso_neto_producto'].strip()
        presentacion = data['presentacion_producto'].strip()
        stock = data['stock_producto'].strip()
        precio = data['precio_producto'].strip()
        imagen = data['imagen_producto']

        if nombre == '' or peso_neto == '' or presentacion == '' or stock == '' or precio == '':
            return 'Debes de llenar todos los campos del formulario.'

        if not 8 <= len(nombre) <= 32:
            return 'El nombre del producto debe de contener entre 8 y 128 caracteres.'
        elif not 3 <= len(peso_neto) <= 8:
            return 'El peso neto del producto debe de contener entre 3 y 8 caracteres.'
        elif not 5 <= len(presentacion) <= 16:
            return 'La presentación del producto debe de contener entre 5 y 16 caracteres.'

        try:
            stock = int(stock)
        except ValueError:
            return 'El stock debe de ser un número entero.'

        try:
            precio = Decimal(precio)
        except InvalidOperation:
            return 'El precio debe de ser un número entero o decimal.'

        if stock < 0:
            return 'El stock no puede ser menor que 0.'
        elif precio <= Decimal(0):
            return 'El precio no puede ser menor o igual que 0.'

        if imagen != b'':
            if imagen.headers['Content-Type'] not in ('image/png', 'image/jpeg'):
                return 'El formato de la imagen no es correcto. Solo se soporta imágenes .png y .jpeg'

            _imagen = {'imagen': bytearray(b64encode(imagen.file.read()))}
        else:
            _imagen = {}

        verify = await self.verify(nombre, peso_neto, id_producto=id_producto)

        if not verify:
            return 'Ya existe otro producto con el mismo nombre y peso neto.'

        return {'nombre': nombre,
                'peso_neto': peso_neto,
                'presentacion': presentacion,
                'stock': stock,
                'precio': precio,
                **_imagen}

    async def update(self, data, id_producto: int):
        producto_model = self.app.mvc.models['producto']

        return await producto_model.update(data, id_producto)

    async def producto(self, id_: int):
        producto_model = self.app.mvc.models['producto']

        return await producto_model.get(id_)

    async def verify(self, nombre: str, peso_neto: str, id_producto: int = None) -> str:
        producto_model = self.app.mvc.models['producto']

        return await producto_model.verify(nombre, peso_neto, id_producto=id_producto)


class BuscarProductos(Controller):
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_produccion
    async def get(self, request, usuario):
        producto_model = self.app.mvc.models['producto']

        nombres = '%{}%'.format(request.match_info['nombres'].replace('-', ' '))

        query = 'SELECT id_producto, nombre_producto, peso_neto_producto FROM t_producto WHERE '\
                'lower(producto.nombre_producto) LIKE $1 LIMIT 10'

        values = (nombres,)

        results = await producto_model.get_by_name(query, values)

        if results:
            results = [{k: v for k, v in r.items()} for r in results]

        return json_response(json.dumps(results))


class ListarProductos(Controller):
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_produccion
    async def load_more(self, request, usuario):
        pagina = int(request.match_info['pagina'])

        producto_model = self.app.mvc.models['producto']

        productos = await producto_model.get_chunk(10, pagina)

        if productos:
            productos = [{k: v for k, v in r.items()} for r in productos]

        return json_response(json.dumps(productos))
    
    @template('mantener.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_produccion
    async def get(self, request, usuario):
        results_buttons = (
            {
                'name': 'Buscar',
                'href': '/producto/buscar',
                'class': 'primary',
                'selector': 'search_btn',
            },
            {
                'name': 'Registrar nuevo',
                'href': '/producto/nuevo',
                'class': 'primary',
                'selector': 'register_btn'
            },
            {
                'name': 'Modificar',
                'href': '/producto/modificar',
                'class': 'primary',
                'selector': 'update_btn'
            }
        )

        results_search = {
            'title': 'Buscar producto',
            'input': 'nombres',
            'href': '/producto/buscar'
        }

        results_header = ('#', 'Nombre', 'Peso neto', 'Presentación', 'Stock', 'Precio')

        return {'usuario': usuario,
                'mantenimiento': 'producto',
                'results_title': 'Gestionar productos',
                'results_search': results_search,
                'results_buttons': results_buttons,
                'results_header': results_header,
                'results': (await self.get_chunk())}

    async def get_chunk(self, amount: int = 10, offset: int = 0):
        producto_model = self.app.mvc.models['producto']

        return await producto_model.get_chunk(amount, offset)
