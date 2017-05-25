import asyncio
import asyncpg
from typing import Union

DSN = 'postgresql://{user}:{password}@{host}:{port}/{database}'


class Connection:
    def __init__(self, host: str, port: int, user: str, password: str, database: str, schema: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.schema = schema

        self.dsn = self._parse_dsn()
        self.pool = None

    async def start(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(dsn=self.dsn)

    async def query(self, query: str,  values: Union[tuple, list] = None, first: bool = False):
        async with self.pool.acquire() as connection:
            prepared_stmt = await connection.prepare(self._add_schema(query))

            strat = 'fetch'

            if first:
                strat = 'fetchrow'

            fetch_query = getattr(prepared_stmt, strat)

            if values:
                return await fetch_query(*values)

            return await fetch_query()

    async def update(self, queries: Union[tuple, list], values: Union[tuple, list] = None):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                queries = map(lambda query: self._add_schema(query), queries)

                try:
                    for index, query in enumerate(queries):
                        query = self._add_schema(query)
                        if values[index]:
                            await connection.execute(query, *values[index])
                        else:
                            await connection.execute(query)

                    return True
                except:
                    pass
        return False

    def _add_schema(self, query):
        return query.replace('t_', self.schema + '.')

    def _parse_dsn(self):
        return DSN.format(user=self.user, password=self.password, host=self.host, port=self.port,
                          database=self.database)
