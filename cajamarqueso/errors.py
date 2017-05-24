
__all__ = ['LoaderException',
           'ControllersIterableNotFound',
           'ModelCallableNotFound',
           'SetupRoutesFunctionNotFound']


class LoaderException(Exception):
    """
    Excepción tirada por el Loader.
    """
    pass


class SetupRoutesFunctionNotFound(LoaderException):
    """
    No se encontró la función setup_routes.
    """
    pass


class ModelCallableNotFound(LoaderException):
    """
    Callable de modelo no encontrado.
    """
    pass


class ControllersIterableNotFound(LoaderException):
    """
    Tuple o List Controllers no encontrado.
    """
    pass
