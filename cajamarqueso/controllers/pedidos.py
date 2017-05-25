from enum import Enum
from aiohttp_jinja2 import template

from ..abc import Controller

Controllers = ('GenerarPedido', 'RegistrarPago', 'ListarPedidos')


class EstadoPedido(Enum):
    PAGADO = 1
    NO_PAGADO = 2


class GenerarPedido(Controller):
    @template('pedidos/generar.html')
    async def show(self, request):
        return {
            'productos': await self.get_productos()
        }

    @template('pedidos/generar.html')
    async def show_with(self, request):
        data = await request.post()
        return {
            'cliente': await self.get_cliente(data['id_cliente']),
            'productos': await self.get_productos()
        }

    async def get_cliente(self, id: str):
        # Modelo de cliente
        cliente_model = self.app.mvc.models['cliente']

        # Id de cliente
        id = int(id)

        return await cliente_model.get(id)

    async def get_productos(self):
        # Modelo de producto
        producto_model = self.app.mvc.models['producto']

        return await producto_model.get_all()


class RegistrarPago(Controller):
    pass


class ListarPedidos(Controller):
    pass
