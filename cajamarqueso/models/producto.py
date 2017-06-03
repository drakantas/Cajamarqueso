from ..abc import Model


class Producto(Model):
    async def get_all(self):
        return await self.db.query('SELECT * FROM t_producto ORDER BY producto.id_producto DESC')

    async def get(self, id_: int):
        return await self.db.query('SELECT * FROM t_producto WHERE id_producto = $1', values=(id_,), first=True)
