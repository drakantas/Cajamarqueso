from os import listdir
from os.path import isfile
from jinja2 import FileSystemLoader
from aiohttp.web import Application
from aiohttp_jinja2 import setup

from .db import Connection
from .mvc import Mvc
from .router import Router

try:
    import ujson as json
except ImportError:
    import json


class Cajamarqueso(Application):
    def __init__(self, paths: dict):
        # Rutas de la aplicación
        self.paths = paths

        self.db_config = dict()

        with open(self.paths['config'].joinpath('db.json')) as db_cf:
            self.db_config = json.load(db_cf)

        self._router = Router()

        # Rutas a archivos estáticos
        self._router.add_static('/static', self.paths['static'])

        # Interfaz de la base de datos
        self.db = Connection(self.db_config['host'], self.db_config['port'], self.db_config['user'],
                             self.db_config['password'], self.db_config['database'], self.db_config['schema'])

        self.mvc = Mvc(self, self._router, self.db, path=self.paths['app'])

        super().__init__(router=self._router)

        # Inicializar el sistema de templates Jinja2
        setup(self, loader=FileSystemLoader(str(self.paths['resources'].joinpath('views').resolve())))

    async def startup(self):
        # Iniciar conexión con la base de datos
        await self.db.start()

        await super().startup()
