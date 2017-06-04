from typing import Union

from ..abc import Model
from ..date import date
from ..controllers.usuarios import TiposUsuario


class Usuario(Model):
    async def get_by_name(self, query: str, values: Union[list, tuple]):
        return await self.db.query(query, values=values)

    async def get(self, id_: Union[int, str]) -> Union[bool, dict]:
        if isinstance(id_, str):
            where_clause = 'WHERE email = $1'
        elif isinstance(id_, int):
            where_clause = 'WHERE dni = $1'
        else:
            return False

        query = 'SELECT * FROM t_usuario ' + where_clause

        result = await self.db.query(query, values=(id_,), first=True)

        if not result:
            return False

        result = {k: v for k, v in result.items()}
        result['credencial'] = result['credencial'].encode('utf-8')

        return result

    async def get_chunk(self, chunk: int, offset: int) -> Union[list, bool]:
        query = 'SELECT dni, email, fecha_registro, nombres, apellidos, tipo_usuario FROM t_usuario ORDER BY ' \
                'fecha_registro DESC LIMIT $1 OFFSET $2'

        values = (chunk, chunk * offset)

        results = await self.db.query(query, values=values)
        results = [{k: v for k, v in r.items()} for r in results]

        if results:
            for result in results:
                result['tipo_usuario'] = await self.get_user_type(result['tipo_usuario'])
                result['fecha_registro'] = await date().parse(result['fecha_registro'])
            return results

        return False

    async def get_user_type(self, id_: int) -> str:
        if id_ not in (tipo.value for tipo in TiposUsuario):
            return 'Invalido'

        if id_ == TiposUsuario.ADMINISTRADOR.value:
            return 'Administrador'
        elif id_ == TiposUsuario.ENCARGADO_VENTAS.value:
            return 'Encargado de ventas'
        elif id_ == TiposUsuario.ENCARGADO_PRODUCCION.value:
            return 'Encargado de producción'
