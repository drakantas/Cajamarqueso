from ..router import Router
from ..controllers.pedidos import COD_PEDIDO_PATTERN


def setup_routes(router: Router):
    router.add_route('GET', '/pedido/nuevo', 'pedidos.GenerarPedido.show')
    router.add_route('POST', '/pedido/nuevo', 'pedidos.GenerarPedido.show_with')
    router.add_route('POST', '/pedido/registrar-nuevo', 'pedidos.GenerarPedido.register')

    router.add_route('POST', '/pedidos', 'pedidos.BuscarPedido.show_results')

    router.add_resource(r'/pedido/registrar-pago/{cod_pedido:' + COD_PEDIDO_PATTERN + '}')\
          .add_route('GET', getattr(router.controllers['pedidos.RegistrarPago'], 'show'))
    router.add_resource(r'/pedido/registrar-pago/{cod_pedido:' + COD_PEDIDO_PATTERN + '}')\
          .add_route('POST', getattr(router.controllers['pedidos.RegistrarPago'], 'post'))

    router.add_resource(r'/pedido/pagado/{cod_pedido:' + COD_PEDIDO_PATTERN + '}')\
          .add_route('GET', getattr(router.controllers['pedidos.GenerarPedido'], 'after_registration'))

    router.add_resource(r'/pedido/actualizar/{cod_pedido:' + COD_PEDIDO_PATTERN + '}') \
          .add_route('GET', getattr(router.controllers['pedidos.ActualizarPedido'], 'show'))
    router.add_resource(r'/pedido/actualizar/{cod_pedido:' + COD_PEDIDO_PATTERN + '}') \
          .add_route('POST', getattr(router.controllers['pedidos.ActualizarPedido'], 'post'))
