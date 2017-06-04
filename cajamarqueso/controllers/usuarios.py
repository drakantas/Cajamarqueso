from enum import Enum
from bcrypt import hashpw, gensalt
from typing import Union
from aiohttp.web import HTTPFound, json_response
from aiohttp_jinja2 import template

from ..abc import Controller
from ..date import date
from ..decorators import get_usuario, usuario_debe_estar_conectado, usuario_debe_no_estar_conectado, solo_admin

try:
    import ujson as json
except ImportError:
    import json

Controllers = ('IniciarSesion', 'CerrarSesion', 'LandingPage', 'ListarUsuarios', 'BuscarUsuarios')


class TiposUsuario(Enum):
    ADMINISTRADOR = 1
    ENCARGADO_VENTAS = 2
    ENCARGADO_PRODUCCION = 3


class LandingPage(Controller):
    @template('bienvenido.html')
    async def get(self, request):
        _session = await self.get_session(request)

        if 'usuario' in _session:
            return {'usuario': _session['usuario']}

        raise HTTPFound('/login')


class BuscarUsuarios(Controller):
    @get_usuario
    @usuario_debe_estar_conectado
    @solo_admin
    async def get(self, request, usuario):
        usuario_model = self.app.mvc.models['usuario']
        nombres = '%{}%'.format(request.match_info['nombres'].replace('-', ' '))

        query = 'SELECT dni, nombres, apellidos FROM t_usuario WHERE lower(usuario.nombres) LIKE $1 LIMIT 10'
        values=(nombres,)

        results = await usuario_model.get_by_name(query, values)

        if results:
            results = [{k: v for k, v in r.items()} for r in results]

        return json_response(json.dumps(results))


class ListarUsuarios(Controller):
    @get_usuario
    @usuario_debe_estar_conectado
    @solo_admin
    async def load_more(self, request, usuario):
        pagina = int(request.match_info['pagina'])

        usuario_model = self.app.mvc.models['usuario']

        usuarios = await usuario_model.get_chunk(10, pagina)

        if usuarios:
            usuarios = [{k: v for k, v in r.items()} for r in usuarios]

        return json_response(json.dumps(usuarios))

    @template('mantener.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @solo_admin
    async def get(self, request, usuario):
        results_buttons = (
            {
                'name': 'Buscar',
                'href': '/usuario/buscar',
                'class': 'primary',
                'selector': 'search_btn',
            },
            {
                'name': 'Registrar nuevo',
                'href': '/usuario/nuevo',
                'class': 'primary',
                'selector': 'register_btn'
            },
            {
                'name': 'Modificar',
                'href': '/usuario/modificar',
                'class': 'primary',
                'selector': 'update_btn'
            },
            {
                'name': 'Eliminar',
                'href': '/usuario/eliminar',
                'class': 'danger',
                'selector': 'remove_btn'
            }
        )

        results_search = {
            'title': 'Buscar usuario',
            'input': 'nombres',
            'href': '/usuario/buscar'
        }
        results_header = ('DNI', 'Correo electrónico', 'Tipo de usuario', 'Fecha de registro', 'Nombres', 'Apellidos')

        return {'usuario': usuario,
                'mantenimiento': 'usuario',
                'results_title': 'Gestionar usuarios',
                'results_search': results_search,
                'results_buttons': results_buttons,
                'results_header': results_header,
                'results': (await self.get_chunk())}

    async def get_chunk(self, amount: int = 10, offset: int = 0):
        usuario_model = self.app.mvc.models['usuario']

        return await usuario_model.get_chunk(amount, offset)


class IniciarSesion(Controller):
    @template('usuarios/login.html')
    @get_usuario
    @usuario_debe_no_estar_conectado
    async def get(self, request, usuario):
        return

    @template('usuarios/login.html')
    @get_usuario
    @usuario_debe_no_estar_conectado
    async def post(self, request, usuario):
        data = await request.post()

        validated_data = await self.validate(data)

        if isinstance(validated_data, str):
            return {'error': validated_data}

        await self.init_session(request, validated_data)

        return HTTPFound('/')

    async def validate(self, data) -> Union[str, int]:
        if data['email'] == '':
            return 'Debes de llenar el campo de correo electrónico.'
        elif data['password'] == '':
            return 'Debes de llenar el campo de contraseña.'

        if not 16 < len(data['email']) < 128:
            return 'El campo de correo electrónico debe contener entre 16 y 128 caracteres.'
        elif not 8 < len(data['password']) < 32:
            return 'El campo de contraseña debe contener entre 8 y 32 caracteres.'

        user = await self.get_user_by_email(data['email'])

        error_message = 'El correo electrónico o contraseña no coinciden, inténtelo otra vez.'

        if not user:
            return error_message

        _p = data['password'].encode('utf-8')

        if hashpw(_p, user['credencial']) != user['credencial']:
            return error_message

        return user['dni']

    async def init_session(self, request, user_id: int):
        _session = await self.get_session(request)

        user = await self.get_user_by_id(user_id)

        user_state = {
            'dni': user['dni'],
            'email': user['email'],
            'fecha_registro': (await date().parse(user['fecha_registro'])),
            'nombres': user['nombres'],
            'apellidos': user['apellidos'],
            'tipo': user['tipo_usuario']
        }

        _session['usuario'] = user_state

    async def get_user_by_email(self, email: str):
        usuario_model = self.app.mvc.models['usuario']

        return await usuario_model.get(email)

    async def get_user_by_id(self, id_: int):
        usuario_model = self.app.mvc.models['usuario']

        return await usuario_model.get(id_)


class CerrarSesion(Controller):
    @get_usuario
    @usuario_debe_estar_conectado
    async def get(self, request, usuario):
        _session = await self.get_session(request)

        del _session['usuario']

        return HTTPFound('/')
