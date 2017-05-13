from os import listdir
from os.path import isfile
from sys import modules
from importlib import import_module
from aiohttp.web import Application
from .router import Router
from .errors import MissingSetupRoutes

CONTROLLERS_PATH = 'cajamarqueso.controllers.{name}'
ROUTES_PATH = 'cajamarqueso.routes.{name}'


class Cajamarqueso(Application):

    def __init__(self, paths: dict):
        # Rutas de la aplicación
        self.paths = paths
        self.paths['routes'] = self.paths['app'].joinpath('routes')
        self.paths['controllers'] = self.paths['app'].joinpath('controllers')

        # Controladores
        self.controllers = dict()

        super().__init__(router=Router(self.controllers))

        self.load_controllers()

        self.load_routes()

    def load_routes(self):
        self._load('routes')

    def load_controllers(self):
        self._load('controllers')

    def _load(self, name: str):
        for file in listdir(self.paths[name]):
            if not isfile(file) and not file.endswith('.py'):
                continue

            getattr(self, '_load_{name}'.format(name=name[:-1]))(file[:-3])

    def _load_route(self, name: str):
        # Importar el modulo
        lib = import_module(ROUTES_PATH.format(name=name))

        # Revisar que existe la función setup_routes
        if not hasattr(lib, 'setup_routes') and type(getattr(lib, 'setup_routes')).__name__ != 'function':
            del lib
            del modules[name]
            raise MissingSetupRoutes('No se encontró la función setup_routes() en {}'.format(name))

        # Pasar el router como único argumento
        lib.setup_routes(self.router)

    def _load_controller(self, name: str):
        # Importar controlador
        _module = import_module(CONTROLLERS_PATH.format(name=name))

        # Clase del controlador
        _class = getattr(_module, name.capitalize())

        controller = {
            name: _class(app=self)
        }

        self.controllers.update(controller)
