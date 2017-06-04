from ..router import Router


def setup_routes(router: Router):
    router.add_route('GET', '/productos', 'productos.ListarProductos.get')

    router.add_resource(r'/producto/buscar/{nombres:[a-zA-Z\-0-9]+}') \
          .add_route('POST', getattr(router.controllers['productos.BuscarProductos'], 'get'))

    router.add_resource(r'/productos/cargar-mas/{pagina:[1-9][0-9]*}') \
          .add_route('GET', getattr(router.controllers['productos.ListarProductos'], 'load_more'))
