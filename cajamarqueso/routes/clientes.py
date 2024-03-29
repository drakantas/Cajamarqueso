from ..router import Router


def setup_routes(router: Router):
    router.add_resource(r'/buscar-cliente/{search_type:(?:cod|nom)}/{search_query:[\w\-]+}')\
          .add_route('POST', getattr(router.controllers['clientes.BuscarCliente'], 'search'))

    router.add_route('GET', '/clientes', 'clientes.ListarClientes.get')

    router.add_resource(r'/cliente/buscar/{nombres:[a-zA-Z\-0-9]+}')\
          .add_route('POST', getattr(router.controllers['clientes.BuscarClientes'], 'get'))

    router.add_resource(r'/clientes/cargar-mas/{pagina:[1-9][0-9]*}')\
          .add_route('GET', getattr(router.controllers['clientes.ListarClientes'], 'load_more'))

    router.add_route('GET', '/cliente/nuevo', 'clientes.GestionarCliente.register_get')
    router.add_route('POST', '/cliente/nuevo', 'clientes.GestionarCliente.register_post')

    router.add_resource(r'/cliente/modificar/{id_cliente:[1-9][0-9]+}') \
          .add_route('GET', getattr(router.controllers['clientes.GestionarCliente'], 'update_get'))

    router.add_resource(r'/cliente/modificar/{id_cliente:[1-9][0-9]+}') \
          .add_route('POST', getattr(router.controllers['clientes.GestionarCliente'], 'update_post'))
