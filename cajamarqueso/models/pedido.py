from typing import Union
from decimal import Decimal
from datetime import datetime

from ..abc import Model
from ..date import date
from ..controllers.pedidos import EstadoPedido, EntregaPedido

COD_PEDIDO_FORMAT = 'PED{nro_ped}'
COD_COMPROBANTE_FORMAT = 'PAG{fecha}{pedido}'


class Pedido(Model):
    async def get_pedidos(self, id_cliente: int, estado_importa: bool = False) -> list:
        pedidos = await self.db.query('SELECT cod_pedido, cliente_id, fecha_realizado, estado, entrega, '
                                      'sum(detalle_pedido.cantidad * (SELECT precio FROM t_producto WHERE '
                                      'id_producto = detalle_pedido.producto_id)) as importe_total FROM t_pedido '
                                      'LEFT JOIN t_detalle_pedido ON detalle_pedido.pedido_cod = pedido.cod_pedido '
                                      'WHERE cliente_id = $1 GROUP BY cod_pedido ORDER BY fecha_realizado DESC',
                                      (id_cliente,))
        results = list()

        for pedido in pedidos:
            if estado_importa:
                if pedido['estado'] == 1:
                    continue

            result = {k: v for k, v in pedido.items()}

            result['fecha_realizado'] = await date().parse(result['fecha_realizado'])
            result['detalles'] = [{k: v for k, v in detalle.items()}
                                  for detalle in (await self.get_detalles(pedido['cod_pedido']))]
            results.append(result)

        return results

    async def get(self, cod_pedido: str) -> Union[dict, None]:
        pedido = await self.db.query('SELECT * FROM t_pedido WHERE cod_pedido = $1', (cod_pedido,), first=True)

        if not pedido:
            return None

        cliente = await self.db.query('SELECT * FROM t_cliente WHERE id_cliente = $1', (pedido['cliente_id'],),
                                      first=True)

        pedido = {k: v for k, v in pedido.items()}

        pago = await self.get_payment(pedido['cod_pedido'])

        pedido['up_fecha_realizado'] = pedido['fecha_realizado']
        pedido['fecha_realizado'] = await date().parse(pedido['up_fecha_realizado'])

        pedido.update({
            'cliente': {k: v for k, v in cliente.items()},
            'detalles': [{k: v for k, v in detalle.items()}
                         for detalle in (await self.get_detalles(pedido['cod_pedido']))],
            'pago': {k: v for k, v in pago.items()} if pago else {}
        })

        try:
            pedido['pago']['fecha_realizado'] = await date().parse(pedido['pago']['fecha_realizado'])
        except KeyError:
            pass

        importe_total = 0

        for detalle in pedido['detalles']:
            importe_total += detalle['precio'] * detalle['cantidad']

        pedido['importe_total'] = importe_total

        return pedido

    async def get_payment(self, cod_pedido: str):
        return await self.db.query('SELECT * FROM t_pago WHERE pedido_cod = $1', (cod_pedido,), first=True)

    async def update(self, data: dict, pagado: bool = False) -> bool:
        fecha = (await date().get_code_format(data['ahora']))
        cod_comprobante = COD_COMPROBANTE_FORMAT.format(fecha=fecha, pedido=data['cod_pedido'][3:])

        queries = ['INSERT INTO t_pago (pedido_cod, fecha_realizado, cod_comprobante) VALUES ($1, $2, $3)']
        values = [(data['cod_pedido'], data['ahora'], cod_comprobante)]

        if not pagado:
            queries.append('UPDATE t_pedido SET estado = $1 WHERE cod_pedido = $2')
            values.append((EstadoPedido.PAGADO.value, data['cod_pedido']))

        update_pago = await self.db.update(queries, values)
        update_importe = await self.update_importe_pagado(data['cod_pedido'])

        return update_pago == update_importe

    async def get_detalles(self, cod_pedido: str) -> list:
        detalles = await self.db.query('SELECT * FROM t_detalle_pedido INNER JOIN t_producto ON '
                                       'detalle_pedido.producto_id = producto.id_producto WHERE '
                                       'detalle_pedido.pedido_cod = $1', (cod_pedido,))
        return detalles

    async def get_client_name(self, cod_pedido: str) -> str:
        pedido = await self.get(cod_pedido)

        query = 'SELECT nombre_cliente FROM t_cliente WHERE id_cliente = $1'

        return (await self.db.query(query, values=(pedido['cliente_id'],), first=True))['nombre_cliente']

    async def create(self, data: dict) -> Union[bool, str]:
        pedido = await self.create_pedido(data)

        if not pedido:
            return False

        detalles_queries, detalles_values = list(), list()

        for k, v in data['productos'].items():
            detalle_query = 'INSERT INTO t_detalle_pedido (pedido_cod, producto_id, cantidad) VALUES ($1, $2, $3)'
            detalle_values = (pedido['cod_pedido'], k, v)

            detalles_queries.append(detalle_query)
            detalles_values.append(detalle_values)

            detalle_query = 'UPDATE t_producto SET stock = stock - $1 WHERE id_producto = $2'
            detalle_values = (v, k)

            detalles_queries.append(detalle_query)
            detalles_values.append(detalle_values)

        await self.db.update(detalles_queries, detalles_values)

        if data['estado'] == EstadoPedido.PAGADO.value:
            await self.update({
                'cod_pedido': pedido['cod_pedido'],
                'ahora': data['ahora']
            }, pagado=True)

        return pedido['cod_pedido']

    async def create_pedido(self, data: dict):
        ultimo_pedido = await self.get_last_pedido()

        if ultimo_pedido:
            id_pedido = int(ultimo_pedido['cod_pedido'][3:]) + 1
            cod_pedido = COD_PEDIDO_FORMAT.format(nro_ped=str(id_pedido).zfill(3))
        else:
            cod_pedido = COD_PEDIDO_FORMAT.format(nro_ped='001')

        pedido_query = 'INSERT INTO t_pedido (cod_pedido, cliente_id, estado, entrega, fecha_realizado, subtotal, ' \
                       'igv, importe_pagado) VALUES ($1, $2, $3, $4, $5, 0.0, 0.0, 0.0)'
        pedido_values = (cod_pedido, data['id_cliente'], data['estado'], data['entrega'], data['ahora'])

        new_pedido = await self.db.update((pedido_query,), values=(pedido_values,))

        pedido = await self.db.query('SELECT * FROM t_pedido WHERE cod_pedido = $1', values=(cod_pedido,), first=True)

        return pedido if new_pedido else False

    async def update_importe_pagado(self, cod_pedido: str) -> bool:
        detalles = await self.get_detalles(cod_pedido)
        monto_total = Decimal(0.0)

        for detalle in detalles:
            monto_total += detalle['precio'] * detalle['cantidad']

        igv = monto_total * Decimal(0.18)
        subtotal = round(monto_total - igv, 2)
        igv = round(igv, 2)

        query = 'UPDATE t_pedido SET subtotal = $1, igv = $2, importe_pagado = $3 WHERE cod_pedido = $4'
        return await self.db.update((query,), values=((subtotal, igv, monto_total, cod_pedido),))

    async def update_pedido(self, cod_pedido: str, estado_pedido: int, entrega_pedido: int) -> bool:
        query = 'UPDATE t_pedido SET estado = $1, entrega = $2 WHERE cod_pedido = $3'
        values = (estado_pedido, entrega_pedido, cod_pedido)

        update_pedido = await self.db.update((query,), values=(values,))

        if estado_pedido == EstadoPedido.NO_PAGADO.value:
            queries = ('UPDATE t_pedido SET subtotal = 0.0, igv = 0.0, importe_pagado = 0.0 WHERE cod_pedido = $1',
                       'DELETE FROM t_pago WHERE pedido_cod = $1')
            values = ((cod_pedido,), (cod_pedido,))

            update_ingresos = await self.db.update(queries, values=values)

            return update_pedido == update_ingresos
        else:
            pago = await self.get_payment(cod_pedido)
            update_pago = True

            if not pago:
                update_pago = await self.update({'cod_pedido': cod_pedido, 'ahora': (await date().now())}, pagado=True)

            return update_pedido == update_pago


    async def update_detalles(self, cod_pedido: str, data: dict, new_data: dict):
        # Listas con las consultas que se realizarán
        to_del, to_upd, to_add = list(), list(), list()

        _data = {}

        for detalle in data:
            _data[detalle['producto_id']] = detalle['cantidad']

        data = _data

        for producto_id, cantidad in new_data.items():
            # Nuevo detalle
            if producto_id not in data.keys():
                to_add.append((
                    'INSERT INTO t_detalle_pedido (pedido_cod, producto_id, cantidad) VALUES ($1, $2, $3)',
                    (cod_pedido, producto_id, cantidad)))
                to_upd.append((
                    'UPDATE t_producto SET stock = stock - $1 WHERE id_producto = $2',
                    (cantidad, producto_id)))
            else:
                if data[producto_id] == cantidad:
                    continue

                to_upd.append((
                    'UPDATE t_detalle_pedido SET cantidad = $1 WHERE pedido_cod = $2 AND producto_id = $3',
                    (cantidad, cod_pedido, producto_id)))
                to_upd.append((
                    'UPDATE t_producto SET stock = stock + $1 WHERE id_producto = $2',
                    (data[producto_id] - cantidad, producto_id)))

        for producto_id, cantidad in {k: v for k, v in data.items() if k not in new_data.keys()}.items():
            to_del.append((
                'DELETE FROM t_detalle_pedido WHERE pedido_cod = $1 AND producto_id = $2',
                (cod_pedido, producto_id)))
            to_upd.append((
                'UPDATE t_producto SET stock = stock + $1 WHERE id_producto = $2',
                (cantidad, producto_id)))

        queries = list()
        queries.extend(to_add)
        queries.extend(to_upd)
        queries.extend(to_del)

        values = [query[1] for query in queries]
        queries = [query[0] for query in queries]

        update_detalles = await self.db.update(queries, values=values)
        update_importe_pagado = await self.update_importe_pagado(cod_pedido)

        return update_detalles and update_importe_pagado

    async def get_last_pedido(self):
        query = 'SELECT * FROM t_pedido ORDER BY pedido.fecha_realizado DESC'
        return await self.db.query(query, first=True)

    async def get_all_from_month(self, mes: int):
        query = 'SELECT * FROM t_pedido LEFT JOIN t_pago ON pago.pedido_cod = pedido.cod_pedido WHERE ' \
                'EXTRACT(MONTH FROM pedido.fecha_realizado) = $1'
        values = (mes,)

        return await self.db.query(query, values=values)
