from ..router import Router


def setup_routes(router: Router):
    router.add_route('GET', '/pedido/nuevo', 'pedidos.GenerarPedido.show')
    router.add_route('POST', '/pedido/nuevo', 'pedidos.GenerarPedido.show_with')
