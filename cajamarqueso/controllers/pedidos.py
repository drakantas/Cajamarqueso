import re
from enum import Enum
from typing import Union
from decimal import Decimal, InvalidOperation
from aiohttp.web import HTTPNotFound
from aiohttp_jinja2 import template

from ..abc import Controller
from ..date import date

Controllers = ('GenerarPedido', 'RegistrarPago', 'BuscarPedido', 'ActualizarPedido')

PRODUCT_KEY_PATTERN = r'producto_[1-9][0-9]*'
COD_PEDIDO_PATTERN = r'PED0*(?:(?<=0{2})[1-9]{1}|(?<=0{1})[1-9]{2}|(?<=0{0})[1-9]{3,})'


class EstadoPedido(Enum):
    PAGADO = 1
    NO_PAGADO = 2


class EntregaPedido(Enum):
    PENDIENTE = 1
    ENTREGADO = 2
    CANCELADO = 3


class GenerarPedido(Controller):
    @template('pedidos/generar.html')
    async def show(self, request):
        return {
            'productos': await self.get_productos(),
            'ahora': await date().formatted_now()
        }

    @template('pedidos/generar.html')
    async def show_with(self, request):
        data = await request.post()

        return {
            'cliente': await self.get_cliente(data['id_cliente']) if 'id_cliente' in data else None,
            'productos': await self.get_productos(),
            'ahora': await date().formatted_now()
        }

    @template('pedidos/generar.html')
    async def register(self, request):
        data = await request.post()

        post_data = await self.validate(data)

        if isinstance(post_data, str):
            alert = {'error': post_data}
        else:
            post_data = await self.create(post_data)

            if post_data:
                alert = {'success': 'Se ha generado el pedido exitosamente.'}
            else:
                alert = {'error': 'Algo ha sucedido, no se pudo generar el pedido. Por favor, inténtelo más tarde.'}

        return {
            **alert,
            'cliente': await self.get_cliente(data['id_cliente']) if 'id_cliente' in data else None,
            'productos': await self.get_productos(),
            'ahora': await date().formatted_now()
        }

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

        try:
            estado_pedido = int(data['estado_pedido'])
        except ValueError:
            return 'El estado que ha seleccionado no es válido.'

        if estado_pedido not in (e.value for e in EstadoPedido):
            return 'El estado de pedido brindado es incorrecto. Por favor, inténtelo de nuevo.'

        fecha_actual = await date().now()

        return {
            'id_cliente': id_cliente,
            'productos': productos,
            'estado': estado_pedido,
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
    async def show(self, request):
        cod_pedido = request.match_info['cod_pedido']

        pedido = {k: v for k, v in (await self.app.mvc.models['pedido'].get(cod_pedido)).items()}
        pedido['igv'] = pedido['importe_total'] * Decimal(0.18)
        pedido['subtotal'] = round(pedido['importe_total'] - pedido['igv'], 2)
        pedido['igv'] = round(pedido['igv'], 2)

        pago = await self.app.mvc.models['pedido'].get_payment(cod_pedido)

        if (not pedido) or pago:
            raise HTTPNotFound

        return {**pedido, 'ahora_mismo': await date().formatted_now()}

    @template('pedidos/registrar_pago.html')
    async def post(self, request):
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

        return {**pedido, **alert, 'ahora_mismo': await date().formatted_now()}

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
    async def show(self, request):
        cod_pedido = request.match_info['cod_pedido']
        pedido = await self.app.mvc.models['pedido'].get(cod_pedido)

        if not pedido:
            raise HTTPNotFound

        return {**pedido,
                'productos': await getattr(self.app.mvc.controllers['pedidos.GenerarPedido'], 'get_productos')()}

    @template('pedidos/generar.html')
    async def post(self, request):
        data = await request.post()

        detalles = {int(k[9:]): v for k, v in data.items() if re.fullmatch(PRODUCT_KEY_PATTERN, k)}

        id_pedido = int(request.match_info['pedido_id'])
        pedido = await self.app.mvc.models['pedido'].get(id_pedido)
        _detalles = (await self.app.mvc.models['pedido'].get(id_pedido))['detalles']

        if not pedido:
            raise HTTPNotFound

        validate = await self.validate(detalles, {_d['producto_id']: _d['cantidad'] for _d in _detalles})

        alert = {}

        if isinstance(validate, str):
            alert = {'error': validate}
        elif validate is True:

            detalles = {k: int(v) for k, v in detalles.items()}

            result = await self.update(id_pedido, _detalles, detalles)
            if result:
                alert = {'success': 'Se actualizó el pedido exitosamente.'}
            else:
                alert = {'error': 'No se pudo actualizar el pedido, por favor inténtelo más tarde.'}

        # Actualizar pedido con nuevos detalles
        pedido = await self.app.mvc.models['pedido'].get(id_pedido)

        return {**pedido,
                **alert,
                'productos': await getattr(self.app.mvc.controllers['pedidos.GenerarPedido'], 'get_productos')()}

    async def validate(self, data: dict, current_data: dict) -> Union[str, bool]:
        for producto_id, cantidad in data.items():
            try:
                cantidad = int(cantidad)
            except ValueError:
                return 'La cantidad de productos ingresada debe de ser  un número entero mayor que 0.'

            if cantidad <= 0:
                return 'La cantidad de productos ingresada debe de ser  un número entero mayor que 0.'

            if producto_id in current_data.keys():
                producto = await getattr(self.app.mvc.controllers['pedidos.GenerarPedido'], 'get_producto')(producto_id)

                if cantidad > (current_data[producto_id] + producto['stock']):
                    return 'La cantidad de productos ingresada no puede ser mayor al stock disponible y los cantidad ' \
                           'de productos que están registrados en este momento.'

        return True

    async def update(self, id_pedido: int, data: dict, new_data: dict) -> bool:
        pedido_model = self.app.mvc.models['pedido']

        return await pedido_model.update_detalles(id_pedido, data, new_data)


class BuscarPedido(Controller):
    @template('pedidos/resultados.html')
    async def show_results(self, request):
        data = await request.post()

        cliente = await getattr(self.app.mvc.controllers['pedidos.GenerarPedido'], 'get_cliente')(data['id_cliente'])

        return {
            'cliente': cliente,
            'pedidos': await self.get_pedidos(cliente['id_cliente'], estado_importa=False)
        }

    async def get_pedidos(self, id_cliente: Union[str, int], estado_importa: bool = False) -> list:
        pedido_model = self.app.mvc.models['pedido']

        return await pedido_model.get_pedidos(id_cliente, estado_importa=estado_importa)
