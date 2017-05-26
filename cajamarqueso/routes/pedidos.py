from ..router import Router


def setup_routes(router: Router):
    router.add_route('GET', '/pedido/nuevo', 'pedidos.GenerarPedido.show')
    router.add_route('POST', '/pedido/nuevo', 'pedidos.GenerarPedido.show_with')
    router.add_route('POST', '/pedido/registrar-nuevo', 'pedidos.GenerarPedido.register')

    router.add_route('POST', '/pedidos', 'pedidos.BuscarPedido.show_results')

    router.add_resource(r'/pedido/registrar-pago/{pedido_id:[1-9]\d*}')\
          .add_route('GET', getattr(router.controllers['pedidos.RegistrarPago'], 'show'))
    router.add_resource(r'/pedido/registrar-pago/{pedido_id:[1-9]\d*}')\
          .add_route('POST', getattr(router.controllers['pedidos.RegistrarPago'], 'post'))

    router.add_resource(r'/pedido/actualizar/{pedido_id:[1-9]\d*}')\
          .add_route('GET', getattr(router.controllers['pedidos.ActualizarPedido'], 'show'))
