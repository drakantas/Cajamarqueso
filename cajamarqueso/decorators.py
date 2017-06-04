from functools import wraps
from aiohttp.web import Request, HTTPForbidden, HTTPFound
from aiohttp_session import get_session

from enum import Enum


def get_usuario(coro):
    @wraps(coro)
    async def request_handler(*args):
        _request = [e for e in args if isinstance(e, Request)][0]
        _session = await get_session(_request)

        _user = _session['usuario'] if 'usuario' in _session else None
        _args = (*args, _user)

        return await coro(*_args)
    return request_handler


def usuario_debe_estar_conectado(coro):
    @wraps(coro)
    async def request_handler(*args):
        _user = args[len(args) - 1]

        if not _user:
            raise HTTPFound('/')

        return await coro(*args)
    return request_handler


def usuario_debe_no_estar_conectado(coro):
    @wraps(coro)
    async def request_handler(*args):
        _user = args[len(args) - 1]

        if _user:
            raise HTTPForbidden

        return await coro(*args)
    return request_handler


def admin_y_encargado_ventas(coro):
    @wraps(coro)
    async def request_handler(*args):
        _user = args[len(args) - 1]

        if _user['tipo'] not in (1, 2):
            raise HTTPForbidden

        return await coro(*args)
    return request_handler


def admin_y_encargado_produccion(coro):
    @wraps(coro)
    async def request_handler(*args):
        _user = args[len(args) - 1]

        if _user['tipo'] not in (1, 3):
            raise HTTPForbidden

        return await coro(*args)
    return request_handler


def solo_admin(coro):
    @wraps(coro)
    async def request_handler(*args):
        _user = args[len(args) - 1]

        if _user['tipo'] != 1:
            raise HTTPForbidden

        return await coro(*args)
    return request_handler
