import asyncio
from pathlib import Path
from aiohttp import web
from cajamarqueso.app import Cajamarqueso


async def init_app():
    paths = {
        'app': Path('./cajamarqueso'),
        'config': Path('./config'),
        'static': Path('./static'),
        'resources': Path('./resources')
    }
    _app = Cajamarqueso(paths)
    return _app

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    web.run_app(app, host='127.0.0.1', port=80)
