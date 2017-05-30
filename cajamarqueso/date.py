from datetime import datetime
from pytz import timezone


def date():
    return Date()


class Date:
    def __init__(self):
        self.timezone = timezone('America/Lima')
        self.format = ('%Y/%m/%d %H:%M:%S', '%d/%m/%Y %I:%M:%S %p', '%d%m%Y')

    async def now(self) -> datetime:
        dt_now = datetime.utcnow().astimezone(self.timezone).now()
        return dt_now

    async def parse(self, date: datetime) -> str:
        return date.strftime(self.format[1])

    async def formatted_now(self):
        return await self.parse(await self.now())

    async def get_code_format(self, date: datetime) -> str:
        return date.strftime(self.format[2])
