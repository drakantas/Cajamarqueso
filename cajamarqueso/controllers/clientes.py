from enum import Enum
from aiohttp.web import json_response
from aiohttp_jinja2 import template

from ..abc import Controller
from ..decorators import get_usuario, usuario_debe_estar_conectado, admin_y_encargado_ventas

try:
    import ujson as json
except ImportError:
    import json

Controllers = ('BuscarCliente', 'BuscarClientes', 'ListarClientes')


class TipoCliente(Enum):
    PERSONA = 1
    EMPRESA = 2


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

