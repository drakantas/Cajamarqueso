from aiohttp.web import Response

from ..abc import Controller
from ..app import Cajamarqueso

Controllers = ('GenerarPedido', 'RegistrarPago', 'ListarPedidos')


class GenerarPedido(Controller):
    async def show(self, request):
        # Modelo de producto
        producto_model = self.app.mvc.models['producto']

        # Lista de todos los productos
        productos = await producto_model.get_all()

        return Response(text='Bienvenido.')


class RegistrarPago(Controller):
    pass


class ListarPedidos(Controller):
    pass
