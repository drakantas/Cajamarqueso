from ..router import Router


def setup_routes(router: Router):
    router.add_route('GET', '/productos', 'productos.ListarProductos.get')

    router.add_resource(r'/producto/buscar/{nombres:[a-zA-Z\-0-9]+}') \
          .add_route('POST', getattr(router.controllers['productos.BuscarProductos'], 'get'))

    router.add_resource(r'/productos/cargar-mas/{pagina:[1-9][0-9]*}') \
          .add_route('GET', getattr(router.controllers['productos.ListarProductos'], 'load_more'))

    router.add_route('GET', '/producto/nuevo', 'productos.RegistrarProducto.get')
    router.add_route('POST', '/producto/nuevo', 'productos.RegistrarProducto.post')

    router.add_resource(r'/producto/modificar/{id_producto:[1-9][0-9]*}') \
        .add_route('GET', getattr(router.controllers['productos.ModificarProducto'], 'get'))

    router.add_resource(r'/producto/modificar/{id_producto:[1-9][0-9]*}') \
        .add_route('POST', getattr(router.controllers['productos.ModificarProducto'], 'post'))
