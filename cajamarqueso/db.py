import asyncio
import asyncpg

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

    async def query(self, query: str, values: list = None):
        async with self.pool.acquire() as connection:
            prepared_stmt = await connection.prepare(self._add_schema(query))

            if values:
                return await prepared_stmt.fetch(*values)

            return await prepared_stmt.fetch()

    async def update(self, query: str, values: list = None):
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                prepared_stmt = await connection.prepare(self._add_schema(query))

                if values:
                    return await prepared_stmt.execute(*values)

                return await prepared_stmt.execute()

    def _add_schema(self, query):
        return query.replace('t_', self.schema + '.')

    def _parse_dsn(self):
        return DSN.format(user=self.user, password=self.password, host=self.host, port=self.port,
                          database=self.database)
