from aiohttp.web import Response

from ..abc import Controller
from ..app import Cajamarqueso

Controllers = ('GenerarPedido', 'RegistrarPago', 'ListarPedidos')


class GenerarPedido(Controller):
    async def show(self, request):
        model = self.app.mvc.models['pedido']
        print(model)
        return Response(text='Bienvenido.')


class RegistrarPago(Controller):
    pass


class ListarPedidos(Controller):
    pass
