import re
from enum import Enum
from bcrypt import hashpw, gensalt
from typing import Union
from aiohttp.web import HTTPFound, json_response, HTTPNotFound
from aiohttp_jinja2 import template

from ..abc import Controller
from ..date import date
from ..decorators import get_usuario, usuario_debe_estar_conectado, usuario_debe_no_estar_conectado, solo_admin
from ..controllers.clientes import EMAIL_PATTERN

try:
    import ujson as json
except ImportError:
    import json

Controllers = ('IniciarSesion', 'CerrarSesion', 'LandingPage', 'ListarUsuarios', 'BuscarUsuarios', 'GestionarUsuario')


class TiposUsuario(Enum):
    ADMINISTRADOR = 1
    ENCARGADO_VENTAS = 2
    ENCARGADO_PRODUCCION = 3


class GestionarUsuario(Controller):
    @template('usuarios/gestionar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @solo_admin
    async def register_get(self, request, usuario):
        return {'usuario': usuario}

    @template('usuarios/gestionar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @solo_admin
    async def register_post(self, request, usuario):
        data = await request.post()

        validated_data = await self.validate(data)

        if isinstance(validated_data, str):
            alert = {'error': validated_data}
        else:
            create = await self.create(validated_data)

            if create:
                alert = {'success': 'Se ha registrado al usuario exitosamente.'}
            else:
                alert = {'error': 'No se ha podido registrar al usuario. Por favor, inténtelo más tarde.'}

        return {**alert,
                'usuario': usuario}

    @template('usuarios/gestionar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @solo_admin
    async def update_get(self, request, usuario):
        _usuario = await self.get_usuario(request.match_info['id_usuario'])
        _session = await self.get_session(request)
        alert = {}

        if 'update' in _session:
            alert = {'success': _session['update']['success']}
            del _session['update']

        return {**alert,
                'm_usuario': _usuario,
                'usuario': usuario}

    @template('usuarios/gestionar.html')
    @get_usuario
    @usuario_debe_estar_conectado
    @solo_admin
    async def update_post(self, request, usuario):
        _usuario = await self.get_usuario(request.match_info['id_usuario'])
        _session = await self.get_session(request)

        data = await request.post()
        validated_data = await self.validate(data, id_usuario=_usuario['dni'], update=True)

        if isinstance(validated_data, str):
            alert = {'error': validated_data}
        else:
            update = await self.update(validated_data, id_usuario=_usuario['dni'])

            if update:
                update_session_flag = False

                if _usuario['dni'] == usuario['dni']:
                    update_session_flag = True

                _usuario = await self.get_usuario(validated_data['dni'])

                _session['update'] = {
                    'redirect': '/usuario/modificar/{}'.format(_usuario['dni']),
                    'success': 'Se ha actualizado al usuario exitosamente.'
                }

                if update_session_flag:

                    user_state = {
                        'dni': _usuario['dni'],
                        'email': _usuario['email'],
                        'fecha_registro': _usuario['fecha_registro'],
                        'nombres': _usuario['nombres'],
                        'apellidos': _usuario['apellidos'],
                        'tipo': _usuario['tipo_usuario']
                    }
                    _session['usuario'] = user_state
                    usuario = _session['usuario']

                raise HTTPFound(_session['update']['redirect'])
            else:
                alert = {'error': 'No se ha podido actualizar al usuario. Por favor, inténtelo más tarde.'}

        return {**alert,
                'm_usuario': _usuario,
                'usuario': usuario}

    @get_usuario
    @usuario_debe_estar_conectado
    @solo_admin
    async def remove_get(self, request, usuario):
        _usuario = await self.get_usuario(request.match_info['id_usuario'])
        _session = await self.get_session(request)

        _session['update'] = {
            'redirect': '/usuarios'
        }

        if _usuario['dni'] == usuario['dni']:
            _session['update']['error'] = 'No puedes deshabilitar tu misma cuenta.'
            raise HTTPFound(_session['update']['redirect'])

        remove = await self.remove(_usuario['dni'])

        if remove:
            _session['update']['success'] = 'Se ha deshabilitado al usuario exitosamente.'
        else:
            _session['update']['error'] = 'No se pudo deshabilitar al usuario. Por favor, inténtelo más tarde.'

        raise HTTPFound(_session['update']['redirect'])

    async def validate(self, data, id_usuario: int = None, update: bool = False) -> Union[dict, str]:
        dni = data['dni_usuario'].strip()
        tipo = data['tipo_usuario'].strip()
        email = data['email_usuario'].strip()
        password = data['password_usuario'].strip()
        nombres = data['nombres_usuario'].strip()
        apellidos = data['apellidos_usuario'].strip()
        habilitar = True
        fecha_registro = {}

        _error_llenado = 'Debes de llenar todos los campos.'

        if not update:
            if dni == '' or tipo == '' or email == '' or nombres == '' or apellidos == '' or password == '':
                return _error_llenado
        else:
            if dni == '' or tipo == '' or email == '' or nombres == '' or apellidos == '':
                return _error_llenado

        if not 6 <= len(dni) <= 9:
            return 'El DNI del usuario debe contener entre 6 y 9 caracteres.'
        elif not 16 <= len(email) <= 128:
            return 'El correo electrónico debe contener entre 16 y 128 caracteres.'
        elif not 5 <= len(nombres) <= 64:
            return 'El nombre debe contener entre 5 y 64 caracteres.'
        elif not 5 <= len(apellidos) <= 64:
            return 'El apellido debe contener entre 5 y 64 caracteres.'
        elif not update or (update and password != ''):
            if not 8 <= len(password) <= 32:
                return 'El campo de contraseña debe contener entre 8 y 32 caracteres.'
            password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')

        try:
            dni = int(dni)
        except ValueError:
            return 'El DNI debe de contener solo dígitos.'

        _error_tipo = 'El tipo de usuario seleccionado no existe.'

        try:
            tipo = int(tipo)
            if tipo not in (t.value for t in TiposUsuario):
                return _error_tipo
        except ValueError:
            return _error_tipo

        if not re.fullmatch(EMAIL_PATTERN, email):
            return 'El correo electrónico debe ser de la forma email@ejemplo.com'

        _hab_error = 'La opción seleccionada para habilitar el usuario no existe.'

        if 'habilitar_usuario' in data:
            try:
                habilitar = int(data['habilitar_usuario'])
                if habilitar not in (0, 1):
                    return _hab_error
                habilitar = bool(habilitar)
            except ValueError:
                return _hab_error

        if not update and not id_usuario:
            _usuario = await self._get_usuario(dni)
            _usuario_por_email = await self._get_usuario(email)

            if _usuario:
                return 'Ya existe un usuario registrado con este DNI.'
            elif _usuario_por_email:
                return 'Ya existe un usuario registrado con este correo electrónico.'
        else:
            _usuario = await self._get_usuario(dni)
            _usuario_por_email = await self._get_usuario(email)
            _usuario_ahora = await self._get_usuario(id_usuario, raw_date=True)

            if password == '':
                password = _usuario_ahora['credencial']

            if _usuario and _usuario['dni'] != id_usuario:
                return 'El DNI que has ingresado se encuentra en uso por otro cliente.'
            elif _usuario_por_email and _usuario_por_email['email'] != _usuario_ahora['email']:
                return 'El correo electrónico se encuentra en uso por otro cliente.'

            fecha_registro = {'fecha_registro': _usuario_ahora['fecha_registro']}

        return {
            **fecha_registro,
            'dni': dni,
            'email': email,
            'password': password,
            'tipo': tipo,
            'nombres': nombres,
            'apellidos': apellidos,
            'habilitar': habilitar
        }

    async def create(self, data: dict) -> bool:
        usuario_model = self.app.mvc.models['usuario']

        return await usuario_model.create(data)

    async def update(self, data: dict, id_usuario: int) -> bool:
        usuario_model = self.app.mvc.models['usuario']

        return await usuario_model.update(data, id_usuario)

    async def remove(self, id_usuario: int) -> bool:
        usuario_model = self.app.mvc.models['usuario']

        return await usuario_model.remove(id_usuario)

    async def get_usuario(self, id_usuario: str):
        id_usuario = int(id_usuario)

        if not 100000 <= id_usuario <= 999999999:
            raise HTTPNotFound

        usuario = await self._get_usuario(id_usuario)

        if not usuario:
            raise HTTPNotFound

        return usuario

    async def _get_usuario(self, id_usuario: Union[int, str], raw_date: bool = False):
        usuario_model = self.app.mvc.models['usuario']

        usuario = await usuario_model.get(id_usuario)

        if not usuario:
            return usuario

        if not raw_date:
            usuario['fecha_registro'] = await date().parse(usuario['fecha_registro'])

        return usuario


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
        _session = await self.get_session(request)
        alert = {}

        if 'update' in _session:
            if 'error' in _session['update']:
                alert['error'] = _session['update']['error']
            elif 'success' in _session['update']:
                alert['success'] = _session['update']['success']

            del _session['update']

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
                'name': 'Deshabilitar',
                'href': '/usuario/deshabilitar',
                'class': 'danger',
                'selector': 'remove_btn'
            }
        )

        results_search = {
            'title': 'Buscar usuario',
            'input': 'nombres',
            'href': '/usuario/buscar'
        }
        results_header = ('DNI', 'Correo electrónico', 'Tipo de usuario', 'Fecha de registro', 'Nombres completos',
                          '¿Habilitado?')

        return {**alert,
                'usuario': usuario,
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
        if data['dni'] == '':
            return 'Debes de llenar el campo de dni.'
        elif data['password'] == '':
            return 'Debes de llenar el campo de contraseña.'

        if not 6 <= len(data['dni']) <= 9:
            return 'El campo de dni debe contener entre 6 y 9 caracteres.'
        elif not 8 <= len(data['password']) <= 32:
            return 'El campo de contraseña debe contener entre 8 y 32 caracteres.'

        try:
            dni = int(data['dni'])
        except ValueError:
            return 'Solo debes de ingresar dígitos en el campo de dni. Por favor, inténtelo otra vez.'

        user = await self.get_user_by_id(dni)

        error_message = 'El correo electrónico o contraseña no coinciden, inténtelo otra vez.'

        if not user:
            return error_message

        _p = data['password'].encode('utf-8')

        if hashpw(_p, user['credencial']) != user['credencial']:
            return error_message

        if not user['habilitado']:
            return 'Tu cuenta se encuentra actualmente deshabilitada. Contacta al administrador para reactivar tu ' \
                   'cuenta.'

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
