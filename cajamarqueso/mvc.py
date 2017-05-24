from sys import modules
from pathlib import Path
from typing import Callable, Any
from os import listdir, path
from importlib import import_module

from .errors import *

DIRECTORIES = ('controllers', 'models', 'routes')
ABSOLUTE_PATH = '{path}.{dir}.{module}'


class Mvc:
    def __init__(self, app, router, db, path: Path = Path('.')):
        self.app = app
        self.router = router
        self.db = db
        self.path = path
        self.loader = Loader(self.path)

        self._controllers = dict()
        self._models = dict()
        self._routes = dict()

        self.process_files()

    @property
    def controllers(self):
        return self._controllers

    @property
    def models(self):
        return self._models

    @property
    def routes(self):
        return self._routes

    def process_files(self):
        for _dir in DIRECTORIES:
            _path = self.path.joinpath(_dir)
            for file in listdir(str(_path)):
                if not path.isfile(file) and file[-3:] != '.py':
                    # Si no es un archivo, y no termina en la extensión, proceder con el siguiente
                    continue

                # Quitar la extensión del archivo
                name = file[:-3]

                # Cargar el módulo
                _module = self.loader.load_module(_dir, name, getattr(self.loader,'_check_{}'.format(_dir)))

                # Injectar argumentos
                self.inject(_dir, name, _module)

            if _dir == 'controllers':
                self.router.controllers = self._controllers

    def inject(self, type_: str, name: str, module_):
        _dict = getattr(self, '_' + type_)
        _instance = None

        if type_ == 'controllers':
            controllers = getattr(module_, 'Controllers')

            for controller in controllers:
                _controller = getattr(module_, controller)
                _name = '{file}.{controller}'.format(file=name, controller=controller)
                _dict[_name] = _controller(self.app)

            return

        elif type_ == 'models':
            _instance = getattr(module_, name.capitalize())(self.db)

        elif type_ == 'routes':
            _instance = getattr(module_, 'setup_routes')(self.router)

        _dict[name] = _instance


class Loader:
    def __init__(self, path: Path):
        self.files_path = path
        self.modules_path = self.files_path.resolve().parts[-1]

    def load_module(self, dir_: str, module_: str, predicate: Callable[[Any], bool]):
        _name = self.parse_path(dir_, module_)
        _module = import_module(_name)

        try:
            predicate(_module)
        except LoaderException as e:
            # Mostrar error en Stdout
            print(e)

            # Eliminar trazos de existencia del módulo
            del modules[_name], _module, _name

        return _module

    @staticmethod
    def _check_controllers(module_):
        if not hasattr(module_, 'Controllers') and not isinstance(getattr(module_, 'Controllers'), (tuple, list)):
            raise ControllersIterableNotFound('Iterable "Controllers" del módulo {} no encontrado.'
                                              .format(module_.__name__))
        return True

    @staticmethod
    def _check_models(module_):
        _callable = module_.__name__.split('.')[-1].capitalize()
        if not hasattr(module_, _callable) and not callable(_callable):
            raise ModelCallableNotFound('Callable {} del módulo {} no encontrado.'.format(_callable,
                                                                                          module_.__name__))
        return True

    @staticmethod
    def _check_routes(module_):
        if not hasattr(module_, 'setup_routes') and not isinstance(getattr(module_, 'setup_routes'), function):
            raise SetupRoutesFunctionNotFound('Función setup_routes() del módulo {} no encontrada.'
                                              .format(module_.__name__))
        return True

    def parse_path(self, dir_: str, module_: str) -> str:
        return ABSOLUTE_PATH.format(path=self.modules_path, dir=dir_, module=module_)
