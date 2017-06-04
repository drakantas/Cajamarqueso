from aiohttp_session import get_session

from .app import Cajamarqueso
from .db import Connection


class Controller:
    def __init__(self, app: Cajamarqueso):
        # Instancia de la aplicación
        self.app = app

        # Datos de usuario conectado
        self.usuario = None

    @staticmethod
    async def get_session(request):
        return await get_session(request)


class Model:
    def __init__(self, db: Connection):
        # Interfaz de la base de datos
        self.db = db
