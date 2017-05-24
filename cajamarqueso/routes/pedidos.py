from ..router import Router


def setup_routes(router: Router):
    router.add_route('GET', '/', 'pedidos.GenerarPedido.show')
