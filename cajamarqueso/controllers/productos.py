from aiohttp.web import json_response
from aiohttp_jinja2 import template

from ..abc import Controller
from ..decorators import get_usuario, usuario_debe_estar_conectado, admin_y_encargado_produccion

try:
    import ujson as json
except ImportError:
    import json

Controllers = ('ListarProductos', 'BuscarProductos')


class BuscarProductos(Controller):
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_produccion
    async def get(self, request, usuario):
        producto_model = self.app.mvc.models['producto']

        nombres = '%{}%'.format(request.match_info['nombres'].replace('-', ' '))

        query = 'SELECT id_producto, nombre_producto, variedad_producto FROM t_producto WHERE '\
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

        results_header = ('#', 'Nombre', 'Variedad', 'Presentación', 'Stock', 'Precio')

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
