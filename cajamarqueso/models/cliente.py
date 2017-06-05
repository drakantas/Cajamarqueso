from typing import Union

from ..abc import Model
from ..controllers.clientes import TipoCliente


class Cliente(Model):
    async def search_cliente(self, search_type: str, search_query: str):
        operator = ''

        if search_type == 'cod':
            search_type = 'cliente.id_cliente'
            operator = '='
            try:
                search_query = int(search_query)
            except ValueError:
                return list()
        elif search_type == 'nom':
            search_type = 'lower(cliente.nombre_cliente)'
            operator = 'LIKE'
            search_query = search_query.replace('-', ' ')
            search_query = '%{}%'.format(search_query.lower())

        query = 'SELECT * FROM t_cliente WHERE {search_type} {operator} $1 LIMIT 10'
        query = query.format(search_type=search_type, operator=operator)

        results = await self.db.query(query, values=(search_query,))

        return results

    async def get(self, id_: int):
        return await self.db.query('SELECT * from t_cliente WHERE id_cliente = $1', values=(id_,), first=True)

    async def get_single_by_name(self, name: str):
        query = 'SELECT * from t_cliente WHERE lower(nombre_cliente) = $1'
        values = (name.lower(),)

        return await self.db.query(query, values=values, first=True)

    async def get_by_name(self, query: str, values: Union[list, tuple]):
        return await self.db.query(query, values=values)

    async def create(self, data: dict) -> bool:
        query = ('INSERT INTO t_cliente (id_cliente, nombre_cliente, tipo_cliente, email_cliente, telefono_cliente) '
                 'VALUES ($1, $2, $3, $4, $5)',)
        values = ([v for v in data.values()],)

        return await self.db.update(query, values=values)

    async def update(self, data: dict, id_cliente: int) -> bool:
        query = ('UPDATE t_cliente SET id_cliente = $1, nombre_cliente = $2, tipo_cliente = $3, email_cliente = $4, '
                 'telefono_cliente = $5 WHERE id_cliente = $6',)
        values = [v for v in data.values()]
        values.append(id_cliente)
        values = (values,)

        return await self.db.update(query, values=values)

    async def get_chunk(self, chunk: int, offset: int) -> Union[list, bool]:
        query = 'SELECT id_cliente, nombre_cliente, tipo_cliente, email_cliente, telefono_cliente, (SELECT COUNT(*) '\
                'FROM public.pedido WHERE pedido.cliente_id = cliente.id_cliente) as pedidos_cliente FROM t_cliente '\
                'ORDER BY id_cliente DESC LIMIT $1 OFFSET $2'

        values = (chunk, chunk * offset)

        results = await self.db.query(query, values=values)
        results = [{k: v for k, v in r.items()} for r in results]

        if results:
            for result in results:
                result['tipo_cliente'] = await self.get_client_type(result['tipo_cliente'])
            return results

        return False

    async def get_client_type(self, type_: int) -> str:
        if type_ not in (tipo.value for tipo in TipoCliente):
            return 'Invalido'

        if type_ == TipoCliente.EMPRESA.value:
            return 'Empresa'
        elif type_ == TipoCliente.PERSONA.value:
            return 'Persona'
