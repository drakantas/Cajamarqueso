from ..abc import Model


class Producto(Model):
    async def get_all(self):
        return await self.db.query('SELECT * FROM t_producto')
