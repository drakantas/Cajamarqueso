from enum import Enum
from aiohttp_jinja2 import template

from ..abc import Controller
from ..app import Cajamarqueso

Controllers = ('GenerarPedido', 'RegistrarPago', 'ListarPedidos')


class EstadoPedido(Enum):
    PAGADO = 1
    NO_PAGADO = 2


class GenerarPedido(Controller):
    @template('pedidos/generar.html')
    async def show(self, request):
        # Modelo de producto
        producto_model = self.app.mvc.models['producto']

        # Lista de todos los productos
        productos = await producto_model.get_all()

        return {
            'productos': productos
        }


class RegistrarPago(Controller):
    pass


class ListarPedidos(Controller):
    pass
