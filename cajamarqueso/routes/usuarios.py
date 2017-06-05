from ..router import Router


def setup_routes(router: Router):
    router.add_route('GET', '/', 'usuarios.LandingPage.get')

    router.add_route('GET', '/login', 'usuarios.IniciarSesion.get')
    router.add_route('POST', '/login', 'usuarios.IniciarSesion.post')

    router.add_route('GET', '/logout', 'usuarios.CerrarSesion.get')

    router.add_route('GET', '/usuarios', 'usuarios.ListarUsuarios.get')

    router.add_resource(r'/usuario/buscar/{nombres:[a-zA-Z\-0-9]+}')\
          .add_route('POST', getattr(router.controllers['usuarios.BuscarUsuarios'], 'get'))

    router.add_resource(r'/usuarios/cargar-mas/{pagina:[1-9][0-9]*}')\
          .add_route('GET', getattr(router.controllers['usuarios.ListarUsuarios'], 'load_more'))

    router.add_route('GET', '/usuario/nuevo', 'usuarios.GestionarUsuario.register_get')
    router.add_route('POST', '/usuario/nuevo', 'usuarios.GestionarUsuario.register_post')

    router.add_resource(r'/usuario/modificar/{id_usuario:[1-9][0-9]*}') \
          .add_route('GET', getattr(router.controllers['usuarios.GestionarUsuario'], 'update_get'))

    router.add_resource(r'/usuario/modificar/{id_usuario:[1-9][0-9]*}') \
          .add_route('POST', getattr(router.controllers['usuarios.GestionarUsuario'], 'update_post'))

    router.add_resource(r'/usuario/eliminar/{id_usuario:[1-9][0-9]*}') \
          .add_route('GET', getattr(router.controllers['usuarios.GestionarUsuario'], 'remove_get'))
