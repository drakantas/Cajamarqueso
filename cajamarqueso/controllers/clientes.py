from enum import Enum
from aiohttp.web import json_response
from aiohttp_jinja2 import template

from ..abc import Controller
from ..decorators import get_usuario, usuario_debe_estar_conectado, admin_y_encargado_ventas

try:
    import ujson as json
except ImportError:
    import json

Controllers = ('BuscarCliente',)


class TipoCliente(Enum):
    PERSONA = 1
    EMPRESA = 2


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

