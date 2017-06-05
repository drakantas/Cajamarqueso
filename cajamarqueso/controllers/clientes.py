import re
from enum import Enum
from typing import Union
from aiohttp.web import json_response, HTTPNotFound
from aiohttp_jinja2 import template

from ..abc import Controller
from ..decorators import get_usuario, usuario_debe_estar_conectado, admin_y_encargado_ventas

try:
    import ujson as json
except ImportError:
    import json

Controllers = ('BuscarCliente', 'BuscarClientes', 'ListarClientes', 'GestionarCliente')

EMAIL_PATTERN = r'[a-z0-9\-\.\_]+\@[a-z0-9\-\.\_]+\.[a-z]{2,6}'


class TipoCliente(Enum):
    PERSONA = 1
    EMPRESA = 2


class GestionarCliente(Controller):
    @template('clientes/gestionar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def register_get(self, request, usuario):
        return {'usuario': usuario}

    @template('clientes/gestionar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def register_post(self, request, usuario):
        data = await request.post()

        validated_data = await self.validate(data)

        if isinstance(validated_data, str):
            alert = {'error': validated_data}
        else:
            create = await self.create(validated_data)

            if create:
                alert = {'success': 'Se ha registrado al cliente exitosamente.'}
            else:
                alert = {'error': 'No se pudo registrar al cliente. Por favor, inténtelo más tarde.'}

        return {**alert,
                'usuario': usuario}

    @template('clientes/gestionar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def update_get(self, request, usuario):
        cliente = await self.get_cliente(request.match_info['id_cliente'])

        return {'usuario': usuario,
                'cliente': cliente}

    @template('clientes/gestionar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def update_post(self, request, usuario):
        cliente = await self.get_cliente(request.match_info['id_cliente'])

        data = await request.post()

        validated_data = await self.validate(data, id_cliente=cliente['id_cliente'], update=True)

        if isinstance(validated_data, str):
            alert = {'error': validated_data}
        else:
            update = await self.update(validated_data, cliente['id_cliente'])

            if update:
                cliente = await self.get_cliente(validated_data['id'])
                alert = {'success': 'Se ha actualizado al cliente exitosamente.'}
            else:
                alert = {'error': 'No se pudo actualizar al cliente. Por favor, inténtelo más tarde.'}

        return {**alert,
                'usuario': usuario,
                'cliente': cliente}

    async def create(self, data: dict) -> bool:
        cliente_model = self.app.mvc.models['cliente']

        return await cliente_model.create(data)

    async def update(self, data: dict, id_cliente: int) -> bool:
        cliente_model = self.app.mvc.models['cliente']

        return await cliente_model.update(data, id_cliente)

    async def validate(self, data, id_cliente: int = None, update: bool = False) -> Union[str, dict]:
        _id = data['id_cliente'].strip()
        nombre = data['nombre_cliente'].strip()
        tipo = data['tipo_cliente']
        email = data['email_cliente'].strip()
        telefono = data['telefono_cliente'].strip()

        if _id == '' or nombre == '' or tipo == '' or email == '' or telefono == '':
            return 'Debes de llenar todos los campos.'

        if not 5 < len(nombre) < 128:
            return 'El nombre o razón social del cliente debe contener entre 5 y 128 caracteres.'
        elif not 6 < len(_id) < 11:
            return 'El DNI o RUC del cliente debe contener entre 6 y 11 caracteres.'
        elif not 12 < len(email) < 128:
            return 'El correo electrónico debe contener entre 12 y 128 caracteres.'

        try:
            _id = int(_id)
        except ValueError:
            return 'El DNI o RUC debe de contener solo dígitos'

        if not re.fullmatch(EMAIL_PATTERN, email):
            return 'El correo electrónico debe ser de la forma email@ejemplo.com'

        try:
            telefono = int(telefono)
        except ValueError:
            return 'El teléfono debe contener solo dígitos.'

        if not 10000000 < telefono < 9999999999:
            return 'El número de teléfono debe contener entre 8 y 10 dígitos.'

        _error_tipo = 'El tipo de cliente seleccionado no existe.'

        try:
            tipo = int(tipo)
            if tipo not in (t.value for t in TipoCliente):
                return _error_tipo
        except ValueError:
            return _error_tipo

        if not update and not id_cliente:
            _cliente = await self._get_cliente(_id)
            _cliente_por_nombre = await self._get_cliente_por_nombre(nombre)

            if _cliente:
                return 'Ya existe un cliente con este DNI o RUC.'
            elif _cliente_por_nombre:
                return 'Ya existe un cliente con este nombre o razón social.'
        else:
            cliente = await self._get_cliente(id_cliente)
            _cliente_por_nombre = await self._get_cliente_por_nombre(cliente['nombre_cliente'])

            if _id != id_cliente:
                _cliente = await self._get_cliente(_id)
                if _cliente:
                    return 'El DNI o RUC que has ingresado está en uso por otro cliente'
            elif nombre != cliente['nombre_cliente']:
                _cliente_por_nombre = await self._get_cliente_por_nombre(nombre)
                if _cliente_por_nombre:
                    return 'El nombre o razón social ingresado ya está registrado por otro cliente'

        return {
            'id': _id,
            'nombre': nombre,
            'tipo': tipo,
            'email': email,
            'telefono': str(telefono),
        }

    async def get_cliente(self, id_cliente: str):
        cliente = await self._get_cliente(int(id_cliente))

        if not cliente:
            raise HTTPNotFound

        return cliente

    async def _get_cliente_por_nombre(self, nombre: str):
        cliente_model = self.app.mvc.models['cliente']

        return await cliente_model.get_single_by_name(nombre)

    async def _get_cliente(self, id_cliente: int):
        cliente_model = self.app.mvc.models['cliente']

        return await cliente_model.get(id_cliente)

class BuscarClientes(Controller):
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def get(self, request, usuario):
        cliente_model = self.app.mvc.models['cliente']
        nombres = '%{}%'.format(request.match_info['nombres'].replace('-', ' '))

        query = 'SELECT id_cliente, nombre_cliente FROM t_cliente WHERE lower(cliente.nombre_cliente) LIKE $1 LIMIT 10'
        values=(nombres,)

        results = await cliente_model.get_by_name(query, values)

        if results:
            results = [{k: v for k, v in r.items()} for r in results]

        return json_response(json.dumps(results))


class ListarClientes(Controller):
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def load_more(self, request, usuario):
        pagina = int(request.match_info['pagina'])

        cliente_model = self.app.mvc.models['cliente']

        clientes = await cliente_model.get_chunk(10, pagina)

        if clientes:
            clientes = [{k: v for k, v in r.items()} for r in clientes]

        return json_response(json.dumps(clientes))

    @template('mantener.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def get(self, request, usuario):
        results_buttons = (
            {
                'name': 'Buscar',
                'href': '/cliente/buscar',
                'class': 'primary',
                'selector': 'search_btn',
            },
            {
                'name': 'Registrar nuevo',
                'href': '/cliente/nuevo',
                'class': 'primary',
                'selector': 'register_btn'
            },
            {
                'name': 'Modificar',
                'href': '/cliente/modificar',
                'class': 'primary',
                'selector': 'update_btn'
            }
        )

        results_search = {
            'title': 'Buscar cliente',
            'input': 'nombres',
            'href': '/cliente/buscar'
        }

        results_header = ('DNI/RUC', 'Nombres/Razón social', 'Tipo de cliente', 'Correo electrónico', 'Teléfono',
                          'Pedidos')

        return {'usuario': usuario,
                'mantenimiento': 'cliente',
                'results_title': 'Gestionar clientes',
                'results_search': results_search,
                'results_buttons': results_buttons,
                'results_header': results_header,
                'results': (await self.get_chunk())}

    async def get_chunk(self, amount: int = 10, offset: int = 0):
        cliente_model = self.app.mvc.models['cliente']

        return await cliente_model.get_chunk(amount, offset)


class BuscarCliente(Controller):
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def search(self, request, usuario):
        # Modelo de cliente
        cliente_model = self.app.mvc.models['cliente']

        search_type, search_query = request.match_info['search_type'], request.match_info['search_query']

        results = await cliente_model.search_cliente(search_type, search_query)

        if results:
            def parse_result(result):
                result_dict = dict()

                for k, v in result.items():
                    result_dict[k] = v

                return result_dict

            results = list(map(parse_result, results))

        return json_response(json.dumps(results))

