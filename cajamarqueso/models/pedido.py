from ..abc import Model
from ..date import date


class Pedido(Model):
    async def get_pedidos(self, id_cliente: int, estado_importa: bool = False) -> list:
        pedidos = await self.db.query('SELECT id_pedido, cliente_id, fecha_realizado, estado, '
                                      'sum(detalle_pedido.cantidad * (SELECT precio FROM t_producto WHERE '
                                      'id_producto = detalle_pedido.producto_id)) as importe_total FROM t_pedido '
                                      'LEFT JOIN t_detalle_pedido ON detalle_pedido.pedido_id = pedido.id_pedido '
                                      'WHERE cliente_id = $1 GROUP BY id_pedido ORDER BY fecha_realizado DESC',
                                      (id_cliente,))
        results = list()

        for pedido in pedidos:
            result = dict()

            if estado_importa:
                if pedido['estado'] == 1:
                    continue

            result = {k: v for k, v in pedido.items()}

            result['fecha_realizado'] = await date().parse(result['fecha_realizado'])
            result['detalles'] = [{k: v for k, v in detalle.items()}
                                  for detalle in (await self.get_detalles(pedido['id_pedido']))]
            results.append(result)

        return results

    async def get_detalles(self, id_pedido: int) -> list:
        detalles = await self.db.query('SELECT * FROM t_detalle_pedido WHERE pedido_id = $1', (id_pedido,))
        return detalles

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
