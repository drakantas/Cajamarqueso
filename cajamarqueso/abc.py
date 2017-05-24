from .app import Cajamarqueso
from .db import Connection


class Controller:
    def __init__(self, app: Cajamarqueso):
        # Instancia de la aplicación
        self.app = app


class Model:
    def __init__(self, db: Connection):
        # Interfaz de la base de datos
        self.db = db
