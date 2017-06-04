from typing import Union

from ..abc import Model


class Producto(Model):
    async def get_all(self):
        return await self.db.query('SELECT * FROM t_producto ORDER BY producto.id_producto DESC')

    async def get(self, id_: int):
        return await self.db.query('SELECT * FROM t_producto WHERE id_producto = $1', values=(id_,), first=True)

    async def get_by_name(self, query: str, values: Union[list, tuple]):
        return await self.db.query(query, values=values)

    async def get_chunk(self, chunk: int, offset: int) -> Union[list, bool]:
        query = 'SELECT id_producto, nombre_producto, variedad_producto, presentacion_producto, stock, precio '\
                'FROM t_producto ORDER BY id_producto DESC LIMIT $1 OFFSET $2'

        values = (chunk, chunk * offset)

        results = await self.db.query(query, values=values)
        results = [{k: v for k, v in r.items()} for r in results]

        return results if results else False
