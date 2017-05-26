from ..abc import Model


class Pedido(Model):
    async def create(self, data: dict) -> bool:
        pedido = await self.create_pedido(data)

        if not pedido:
            return False

        detalles_queries, detalles_values = list(), list()

        for k, v in data['productos'].items():
            detalle_query = 'INSERT INTO t_detalle_pedido (pedido_id, producto_id, cantidad) VALUES ($1, $2, $3)'
            detalle_values = (pedido['id_pedido'], k, v)

            detalles_queries.append(detalle_query)
            detalles_values.append(detalle_values)

            detalle_query = 'UPDATE t_producto SET stock = stock - $1 WHERE id_producto = $2'
            detalle_values = (v, k)

            detalles_queries.append(detalle_query)
            detalles_values.append(detalle_values)

        return await self.db.update(detalles_queries, detalles_values)

    async def create_pedido(self, data: dict):
        pedido_query = 'INSERT INTO t_pedido (cliente_id, fecha_realizado, estado) VALUES ($1, $2, $3)'
        pedido_values = (data['id_cliente'], data['ahora'], data['estado'])

        await self.db.update((pedido_query,), (pedido_values,))

        pedido = await self.db.query('SELECT * FROM t_pedido WHERE cliente_id = $1 AND fecha_realizado = $2',
                                    (pedido_values[0], pedido_values[1]), first=True)

        return pedido if pedido else False
