from ..router import Router


def setup_routes(router: Router):
    router.add_resource(r'/buscar-cliente/{search_type:(?:cod|nom)}/{search_query:[\w\-]+}')\
          .add_route('POST', getattr(router.controllers['clientes.BuscarCliente'], 'search'))
