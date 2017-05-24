from aiohttp.web_urldispatcher import UrlDispatcher


class Router(UrlDispatcher):
    def __init__(self):
        super().__init__()

        self._controllers = dict()

    @property
    def controllers(self):
        return self._controllers

    @controllers.setter
    def controllers(self, controllers_: dict):
        self._controllers = controllers_

    def add_route(self, method, path, handler, *, name=None, expect_handler=None):
        if type(handler).__name__ == 'str':
            _module, controller, _method = handler.split('.')
            handler = getattr(self._controllers['{m}.{c}'.format(m=_module, c=controller)], _method)

        return super().add_route(method, path, handler, name=name, expect_handler=expect_handler)
