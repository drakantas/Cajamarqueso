from aiohttp.web_urldispatcher import UrlDispatcher


class Router(UrlDispatcher):

    def __init__(self, controllers: dict):
        super().__init__()

        self.controllers = controllers

    def add_route(self, method, path, handler, *, name=None, expect_handler=None):
        if type(handler).__name__ == 'str':
            controller, _method = handler.split('.')
            handler = getattr(self.controllers[controller], _method)

        return super().add_route(method, path, handler, name=name, expect_handler=expect_handler)
