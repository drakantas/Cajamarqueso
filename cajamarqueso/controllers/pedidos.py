import re
from enum import Enum
from typing import Union
from aiohttp_jinja2 import template

from ..abc import Controller
from ..date import date

Controllers = ('GenerarPedido', 'RegistrarPago', 'BuscarPedido')

PRODUCT_KEY_PATTERN = r'producto_[1-9][0-9]*'


class EstadoPedido(Enum):
    PAGADO = 1
    NO_PAGADO = 2


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
                alert = {'error': 'Algo ha sucedido, no se pudo generar el pedido.'}

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
            return 'El estado de pedido deberá de ser un número entero.'

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
    pass


class BuscarPedido(Controller):
    @template('pedidos/resultados.html')
    async def show_results(self, request):
        data = await request.post()

        cliente = await getattr(self.app.mvc.controllers['pedidos.GenerarPedido'], 'get_cliente')(data['id_cliente'])

        return {
            'cliente': cliente,
            'pedidos': await self.get_pedidos(cliente['id_cliente'], estado_importa=True)
        }

    async def get_pedidos(self, id_cliente: Union[str, int], estado_importa: bool = False) -> list:
        pedido_model = self.app.mvc.models['pedido']

        return await pedido_model.get_pedidos(id_cliente, estado_importa=estado_importa)
