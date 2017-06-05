import re
from enum import Enum
from typing import Union
from decimal import Decimal
from aiohttp.web import HTTPNotFound, HTTPFound
from aiohttp_jinja2 import template

from ..abc import Controller
from ..date import date
from ..decorators import get_usuario, usuario_debe_estar_conectado, solo_admin, admin_y_encargado_ventas

Controllers = ('GenerarPedido', 'RegistrarPago', 'BuscarPedido', 'ActualizarPedido', 'ListarVentas')

PRODUCT_KEY_PATTERN = r'producto_[1-9][0-9]*'
COD_PEDIDO_PATTERN = r'PED0*(?:(?<=0{2})[1-9]{1}|(?<=0{1})[1-9]{2}|(?<=0{0})[1-9]{3,})'


class EstadoPedido(Enum):
    PAGADO = 1
    NO_PAGADO = 2


class EntregaPedido(Enum):
    PENDIENTE = 1
    ENTREGADO = 2
    CANCELADO = 3


def validar_estado(estado: str) -> Union[str, int]:
    try:
        estado_pedido = int(estado)
    except ValueError:
        return 'El estado que ha seleccionado no es válido.'

    if estado_pedido not in (e.value for e in EstadoPedido):
        return 'El estado de pedido brindado es incorrecto. Por favor, inténtelo de nuevo.'

    return estado_pedido


def validar_estado_entrega(entrega: str, validar_completo: bool = False) -> Union[str, int]:
    msg_error_invalido = 'El estado de entrega brindado es incorrecto. Por favor, inténtelo de nuevo.'

    try:
        estado_entrega = int(entrega)
    except ValueError:
        return 'El estado de entrega seleccionado no es válido'

    if not validar_completo:
        if estado_entrega not in (1, 2):
            return msg_error_invalido
    else:
        if estado_entrega not in (e.value for e in EntregaPedido):
            return msg_error_invalido

    return estado_entrega


class GenerarPedido(Controller):
    @template('pedidos/generar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def show(self, request, usuario):
        return {'usuario': usuario,
                'productos': await self.get_productos(),
                'ahora': await date().formatted_now()}

    @template('pedidos/generar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def show_with(self, request, usuario):
        data = await request.post()

        return {'usuario': usuario,
                'cliente': await self.get_cliente(data['id_cliente']) if 'id_cliente' in data else None,
                'productos': await self.get_productos(),
                'ahora': await date().formatted_now()}

    @template('pedidos/generar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def register(self, request, usuario):
        data = await request.post()

        post_data = await self.validate(data)

        if isinstance(post_data, str):
            alert = {'error': post_data}
        else:
            estado_pedido = post_data['estado']

            post_data = await self.create(post_data)

            if post_data:
                alert = {'success': 'Se ha generado el pedido exitosamente con el siguiente código: '
                                    '<strong>{cod}</strong>.'.format(cod=post_data)}

                if estado_pedido == EstadoPedido.PAGADO.value:
                    return HTTPFound('/pedido/pagado/{cod}'.format(cod=post_data))

            else:
                alert = {'error': 'Algo ha sucedido, no se pudo generar el pedido. Por favor, inténtelo más tarde.'}

        return {**alert,
                'usuario': usuario,
                'cliente': await self.get_cliente(data['id_cliente']) if 'id_cliente' in data else None,
                'productos': await self.get_productos(),
                'ahora': await date().formatted_now()}

    @template('pedidos/registrar_pago.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def after_registration(self, request, usuario):
        cod_pedido = request.match_info['cod_pedido']

        pedido = await self.app.mvc.models['pedido'].get(cod_pedido)

        if not pedido:
            raise HTTPNotFound
        elif pedido['estado'] != EstadoPedido.PAGADO.value:
            raise HTTPNotFound
        elif ((await date().now()) - pedido['up_fecha_realizado']).total_seconds() > 15:
            raise HTTPNotFound

        pedido = {k: v for k, v in pedido.items()}

        alert = {'success': 'Se ha generado el pedido exitosamente con el siguiente código: '
                            '<strong>{cod}</strong>.'.format(cod=cod_pedido)}

        return {**pedido, **alert,
                'usuario': usuario,
                'despues_generar': True,
                'ahora_mismo': await date().formatted_now()}

    async def validate(self, data: dict) -> Union[dict, str]:
        try:
            id_cliente = int(data['id_cliente'])
        except ValueError:
            return 'Id de cliente no es un número. Por favor, inténtelo otra vez.'
        except KeyError:
            return 'Debes de haber buscado y seleccionado un cliente antes de realizar esta acción.'

        cliente = await self.get_cliente(id_cliente)

        if not cliente:
            return 'El cliente no existe en nuestra base de datos. Por favor, inténtelo de nuevo con otro cliente.'

        productos = {int(k[9:]): v for k, v in data.items() if re.fullmatch(PRODUCT_KEY_PATTERN, k)}

        if not productos:
            return 'Debes de agregar por lo menos 1 producto al pedido. Por favor, inténtalo de nuevo.'

        for k, v in productos.items():
            try:
                productos[k] = int(v)
            except ValueError:
                return 'Las cantidades de productos deben de ser números enteros.'

            producto = await self.get_producto(k)

            if not producto:
                return 'Uno de los productos ingresados no existe en nuestra base de datos.'

            if producto['stock'] < productos[k]:
                alerta = 'No se tienen suficientes productos en stock para <strong>{nombre}</strong>, solo tenemos ' \
                         '<strong>{stock}</strong> disponibles, y usted trató de registrar {cant}. Por favor, ' \
                         'inténtelo de nuevo.'
                return alerta.format(nombre=producto['nombre_producto'], stock=producto['stock'], cant=v)

        estado_pedido = validar_estado(data['estado_pedido'])
        entrega_pedido = validar_estado_entrega(data['entrega_pedido'])

        if isinstance(estado_pedido, str):
            return estado_pedido
        elif isinstance(entrega_pedido, str):
            return entrega_pedido

        fecha_actual = await date().now()

        return {
            'id_cliente': id_cliente,
            'productos': productos,
            'estado': estado_pedido,
            'entrega': entrega_pedido,
            'ahora': fecha_actual
        }

    async def create(self, data: dict) -> bool:
        # Modelo de pedido
        pedido_model = self.app.mvc.models['pedido']

        return await pedido_model.create(data)

    async def get_cliente(self, id_: Union[str, int]):
        # Modelo de cliente
        cliente_model = self.app.mvc.models['cliente']

        # Id de cliente
        if isinstance(id_, str):
            id_ = int(id_)

        return await cliente_model.get(id_)

    async def get_productos(self):
        # Modelo de producto
        producto_model = self.app.mvc.models['producto']

        return await producto_model.get_all()

    async def get_producto(self, id_: int):
        # Modelo de producto
        producto_model = self.app.mvc.models['producto']

        return await producto_model.get(id_)


class RegistrarPago(Controller):
    @template('pedidos/registrar_pago.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def show(self, request, usuario):
        cod_pedido = request.match_info['cod_pedido']

        pedido = {k: v for k, v in (await self.app.mvc.models['pedido'].get(cod_pedido)).items()}
        pedido['igv'] = pedido['importe_total'] * Decimal(0.18)
        pedido['subtotal'] = round(pedido['importe_total'] - pedido['igv'], 2)
        pedido['igv'] = round(pedido['igv'], 2)

        pago = await self.app.mvc.models['pedido'].get_payment(cod_pedido)

        if (not pedido) or pago:
            raise HTTPNotFound

        return {**pedido,
                'usuario': usuario,
                'ahora_mismo': await date().formatted_now()}

    @template('pedidos/registrar_pago.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def post(self, request, usuario):
        data = await request.post()

        cod_pedido = data['cod_pedido']

        validated_data = await self.validate({
            'cod_pedido': cod_pedido
        })

        if isinstance(validated_data, str):
            alert = {'error': validated_data}
        else:
            status = await self.update(validated_data)

            if status is True:
                alert = {'success': 'Se ha registrado el pago exitosamente.'}
            else:
                alert = {'error': 'No se pudo registrar el pago.'}

        pedido = await self.app.mvc.models['pedido'].get(cod_pedido)

        if not pedido:
            raise HTTPNotFound

        return {**pedido, **alert,
                'usuario': usuario,
                'ahora_mismo': await date().formatted_now()}

    async def validate(self, data: dict):
        cod_pedido = data['cod_pedido']

        if not re.fullmatch(COD_PEDIDO_PATTERN, cod_pedido):
            return 'El código de pedido brindado es incorrecto.'

        pago = await self.app.mvc.models['pedido'].get_payment(cod_pedido)

        if pago:
            return 'Ya existe un pago registrado para este pedido.'

        ahora = await date().now()

        return {
            'cod_pedido': cod_pedido,
            'ahora': ahora
        }

    async def update(self, data: dict):
        pedido_model = self.app.mvc.models['pedido']

        return await pedido_model.update(data)


class ActualizarPedido(Controller):
    @template('pedidos/generar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @solo_admin
    async def show(self, request, usuario):
        cod_pedido = request.match_info['cod_pedido']
        pedido = await self.app.mvc.models['pedido'].get(cod_pedido)

        if not pedido:
            raise HTTPNotFound
        elif pedido['entrega'] == EntregaPedido.CANCELADO.value:
            raise HTTPNotFound

        return {**pedido,
                'usuario': usuario,
                'productos': await getattr(self.app.mvc.controllers['pedidos.GenerarPedido'], 'get_productos')()}

    @template('pedidos/generar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @solo_admin
    async def post(self, request, usuario):
        data = await request.post()

        detalles = {int(k[9:]): v for k, v in data.items() if re.fullmatch(PRODUCT_KEY_PATTERN, k)}

        cod_pedido = request.match_info['cod_pedido']
        pedido = await self.app.mvc.models['pedido'].get(cod_pedido)
        _detalles = (await self.app.mvc.models['pedido'].get(cod_pedido))['detalles']

        if not pedido:
            raise HTTPNotFound

        validate = await self.validate(detalles, {_d['producto_id']: _d['cantidad'] for _d in _detalles},
                                       data['estado_pedido'], data['entrega_pedido'])

        alert = {}

        if isinstance(validate, str):
            alert = {'error': validate}
        elif validate is True:

            detalles = {k: int(v) for k, v in detalles.items()}

            result = await self.update(cod_pedido, _detalles, detalles, data['estado_pedido'], data['entrega_pedido'])
            if result:
                alert = {'success': 'Se actualizó el pedido exitosamente.'}
            else:
                alert = {'error': 'No se pudo actualizar el pedido, por favor inténtelo más tarde.'}

        # Actualizar pedido con nuevos detalles
        pedido = await self.app.mvc.models['pedido'].get(cod_pedido)

        return {**pedido,
                **alert,
                'usuario': usuario,
                'productos': await getattr(self.app.mvc.controllers['pedidos.GenerarPedido'], 'get_productos')()}

    async def validate(self, data: dict, current_data: dict, estado: str, estado_entrega: str) -> Union[str, bool]:
        if not data:
            return 'El pedido debe tener por lo menos un producto. Por favor, inténtalo de nuevo.'

        for producto_id, cantidad in data.items():
            try:
                cantidad = int(cantidad)
            except ValueError:
                return 'La cantidad de productos ingresada debe de ser un número entero mayor que 0.'

            if cantidad <= 0:
                return 'La cantidad de productos ingresada debe de ser un número entero mayor que 0.'

            producto = await getattr(self.app.mvc.controllers['pedidos.GenerarPedido'], 'get_producto')(producto_id)

            if producto_id in current_data.keys():
                if cantidad > (current_data[producto_id] + producto['stock']):
                    return 'La cantidad de productos ingresada por <strong>{name} {pn}</strong> no puede ser mayor al '\
                           'stock disponible y los cantidad de productos que están registrados en este ' \
                           'momento.'.format(name=producto['nombre_producto'], pn=producto['peso_neto_producto'])
            else:
                if cantidad > producto['stock']:
                    return 'La cantidad de productos ingresada por <strong>{name} {pn}</strong> no puede ser mayor al '\
                           'stock disponible.'.format(name=producto['nombre_producto'],
                                                      pn=producto['peso_neto_producto'])

        estado_pedido = validar_estado(estado)
        entrega_pedido = validar_estado_entrega(estado_entrega, validar_completo=True)

        if isinstance(estado_pedido, str):
            return estado_pedido
        elif isinstance(entrega_pedido, str):
            return entrega_pedido

        return True

    async def update(self, cod_pedido: str, data: dict, new_data: dict, estado_pedido: str,
                     entrega_pedido: str) -> bool:
        pedido_model = self.app.mvc.models['pedido']
        estado_pedido = int(estado_pedido)
        entrega_pedido = int(entrega_pedido)

        update_detalles = await pedido_model.update_detalles(cod_pedido, data, new_data)
        update_pedido = await pedido_model.update_pedido(cod_pedido, estado_pedido, entrega_pedido)

        return update_pedido == update_detalles


class BuscarPedido(Controller):
    @template('pedidos/resultados.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @admin_y_encargado_ventas
    async def show_results(self, request, usuario):
        data = await request.post()

        if 'id_cliente' not in data:
            raise HTTPNotFound

        cliente = await getattr(self.app.mvc.controllers['pedidos.GenerarPedido'], 'get_cliente')(data['id_cliente'])

        return {'usuario': usuario,
                'cliente': cliente,
                'pedidos': await self.get_pedidos(cliente['id_cliente'], estado_importa=False)}

    async def get_pedidos(self, id_cliente: Union[str, int], estado_importa: bool = False) -> list:
        pedido_model = self.app.mvc.models['pedido']

        return await pedido_model.get_pedidos(id_cliente, estado_importa=estado_importa)


class ListarVentas(Controller):
    @template('pedidos/ventas.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @solo_admin
    async def get(self, request, usuario):
        ahora = await date().now()
        data = await self.get_data(ahora.month)

        return {**data,
                'usuario': usuario,
                'm': (await self.parse_month(ahora.month)),
                'y': ahora.year}

    @template('pedidos/ventas.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @solo_admin
    async def get_prev_month(self, request, usuario):
        ahora = await date().now()
        if ahora.month != 1:
            mes = ahora.month - 1
        else:
            mes = 1

        data = await self.get_data(mes)

        return {**data,
                'mes_anterior': True,
                'usuario': usuario,
                'm': (await self.parse_month(mes)),
                'y': ahora.year}

    async def get_data(self, mes: int) -> dict:
        pedido_model = self.app.mvc.models['pedido']
        producto_model = self.app.mvc.models['producto']

        pedidos = await pedido_model.get_all_from_month(mes)
        data = {}

        if pedidos:
            pedidos_pagados = 0
            pedidos_pendientes_pago = 0
            pedidos_entregados = 0
            pedidos_pendientes_entrega = 0
            pedidos_cancelados = 0
            ingresos = Decimal(0)
            ingresos_dimpuestos = Decimal(0)
            ingresos_pendientes = Decimal(0)

            for p in pedidos:
                if p['pedido_cod']:
                    pedidos_pagados += 1
                    ingresos += p['importe_pagado']
                    ingresos_dimpuestos += p['subtotal']
                if not p['pedido_cod']:
                    pedidos_pendientes_pago += 1
                    detalles = await pedido_model.get_detalles(p['cod_pedido'])
                    for d in detalles:
                        ingresos_pendientes += Decimal(d['cantidad']) * d['precio']
                if p['entrega'] == 2:
                    pedidos_entregados += 1
                elif p['entrega'] == 1:
                    pedidos_pendientes_entrega += 1
                elif p['entrega'] == 3:
                    pedidos_cancelados += 1

            productos = [{k: v for k, v in p.items()} for p in (await producto_model.get_sales_data(mes))]

            for producto in productos:
                if not producto['cantidad_vendida']:
                    producto['cantidad_vendida'] = 0
                    producto['cantidad_monetaria_vendida'] = 0
                else:
                    producto['cantidad_monetaria_vendida'] = producto['cantidad_vendida'] * producto['precio']

            return {
                'pedidos': pedidos,
                'pedidos_pagados': pedidos_pagados,
                'pedidos_pendientes_pago': pedidos_pendientes_pago,
                'pedidos_entregados': pedidos_entregados,
                'pedidos_pendientes_entrega': pedidos_pendientes_entrega,
                'pedidos_cancelados': pedidos_cancelados,
                'ingresos': ingresos,
                'ingresos_dimpuestos': ingresos_dimpuestos,
                'ingresos_pendientes': ingresos_pendientes,
                'productos': productos
            }

        return {
            'pedidos': list()
        }

    @staticmethod
    async def parse_month(month: int):
        if month == 1:
            return 'Enero'
        elif month == 2:
            return 'Febrero'
        elif month == 3:
            return 'Marzo'
        elif month == 4:
            return 'Abril'
        elif month == 5:
            return 'Mayo'
        elif month == 6:
            return 'Junio'
        elif month == 7:
            return 'Julio'
        elif month == 8:
            return 'Agosto'
        elif month == 9:
            return 'Septiembre'
        elif month == 10:
            return 'Octubre'
        elif month == 11:
            return 'Noviembre'
        elif month == 12:
            return 'Diciembre'
        else:
            return 'WTF'
