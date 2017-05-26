from typing import Union

from ..abc import Model
from ..date import date
from ..controllers.pedidos import EstadoPedido


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

    async def get(self, id_pedido: int) -> Union[dict, None]:
        pedido = await self.db.query('SELECT * FROM t_pedido WHERE id_pedido = $1', (id_pedido,), first=True)

        if not pedido:
            return None

        cliente = await self.db.query('SELECT * FROM t_cliente WHERE id_cliente = $1', (pedido['cliente_id'],),
                                      first=True)

        pedido = {k: v for k, v in pedido.items()}

        pago = await self.get_payment(pedido['id_pedido'])

        pedido['fecha_realizado'] = await date().parse(pedido['fecha_realizado'])

        pedido.update({
            'cliente': {k: v for k, v in cliente.items()},
            'detalles': [{k: v for k, v in detalle.items()} for detalle in (await self.get_detalles(pedido['id_pedido']))],
            'pago': {k: v for k, v in pago.items()} if pago else {}
        })

        importe_total = 0

        for detalle in pedido['detalles']:
            importe_total += detalle['precio'] * detalle['cantidad']

        pedido['importe_total'] = importe_total

        return pedido

    async def get_payment(self, id_pedido: int):
        return await self.db.query('SELECT * FROM t_pago WHERE pedido_id = $1', (id_pedido,), first=True)

    async def update(self, data: dict) -> bool:
        query, values = ('UPDATE t_pedido SET estado = $1 WHERE id_pedido = $2',
                         'INSERT INTO t_pago (pedido_id, importe_pagado, fecha_realizado) '
                         'VALUES ($1, $2, $3)'), ((EstadoPedido.PAGADO.value, data['id_pedido']),
                                                  (data['id_pedido'], data['importe_total'], data['ahora']))

        return await self.db.update(query, values)

    async def get_detalles(self, id_pedido: int) -> list:
        detalles = await self.db.query('SELECT * FROM t_detalle_pedido INNER JOIN t_producto ON '
                                       'detalle_pedido.producto_id = producto.id_producto WHERE '
                                       'detalle_pedido.pedido_id = $1', (id_pedido,))
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
