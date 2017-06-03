from ..abc import Model


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
            search_query = '%{} %'.format(search_query.lower())

        query = 'SELECT * FROM t_cliente WHERE {search_type} {operator} $1'
        query = query.format(search_type=search_type, operator=operator)

        results = await self.db.query(query, values=(search_query,))

        return results

    async def get(self, id_: int):
        return await self.db.query('SELECT * from t_cliente WHERE id_cliente = $1', values=(id_,), first=True)
