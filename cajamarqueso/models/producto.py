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
        query = 'SELECT id_producto, nombre_producto, peso_neto_producto, presentacion_producto, stock, precio '\
                'FROM t_producto ORDER BY id_producto DESC LIMIT $1 OFFSET $2'

        values = (chunk, chunk * offset)

        results = await self.db.query(query, values=values)
        results = [{k: v for k, v in r.items()} for r in results]

        return results if results else False

    async def verify(self, nombre: str, peso_neto: str, id_producto: int = None):
        query = 'SELECT id_producto, nombre_producto, peso_neto_producto, presentacion_producto, stock, precio FROM ' \
                't_producto WHERE nombre_producto = $1 AND peso_neto_producto = $2'
        values = (nombre, peso_neto)

        result = await self.db.query(query, values=values, first=True)

        if not result:
            return True

        if id_producto:
            producto = await self.get(id_producto)

            if (result['nombre_producto'], result['peso_neto_producto']) == (producto['nombre_producto'],
                                                                            producto['peso_neto_producto']):
                return True
            else:
                return False

        return False

    async def create(self, data: dict) -> bool:
        queries = ('INSERT INTO t_producto (nombre_producto, peso_neto_producto, presentacion_producto, stock, '
                   'precio, imagen_producto) VALUES ($1, $2, $3, $4, $5, $6)',)

        values = [(data['nombre'], data['peso_neto'], data['presentacion'], data['stock'], data['precio'],
                   data['imagen'])]

        return await self.db.update(queries, values=values)

    async def update(self, data: dict, id_producto: int) -> bool:
        if 'imagen' not in data.keys():
            query = 'UPDATE t_producto SET nombre_producto = $1, peso_neto_producto = $2, presentacion_producto = $3, ' \
                    'stock = $4, precio = $5 WHERE id_producto = $6'
        else:
            query = 'UPDATE t_producto SET nombre_producto = $1, peso_neto_producto = $2, presentacion_producto = $3, ' \
                    'stock = $4, precio = $5, imagen_producto = $6 WHERE id_producto = $7'

        values = [v for v in data.values()]
        values.append(id_producto)
        values = (values,)

        return await self.db.update((query,), values=values)

    async def get_sales_data(self, month: int):
        query = 'SELECT nombre_producto, peso_neto_producto, precio, (SELECT SUM(cantidad) FROM ' \
                't_detalle_pedido LEFT JOIN t_pedido ON pedido.cod_pedido = detalle_pedido.pedido_cod ' \
                'WHERE producto_id = id_producto AND EXTRACT(MONTH FROM pedido.fecha_realizado) = $1) as ' \
                'cantidad_vendida FROM t_producto'

        return await self.db.query(query, values=(month,))
