from aiohttp.web import Response
from ..controller import Controller


class Pedidos(Controller):
    async def index(self, request):
        print(request.query)
        return Response(text='XD')