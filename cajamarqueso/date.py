from datetime import datetime
from pytz import timezone


def date():
    return Date()


class Date:
    def __init__(self):
        self.timezone = timezone('America/Lima')
        self.format = ('%Y-%m-%d %H:%M:%S', '%d-%m-%Y %I:%M:%S %p')

    async def now(self) -> datetime:
        dt_now = datetime.utcnow().astimezone(self.timezone).now()
        return dt_now

    async def parse(self, date: datetime) -> str:
        return date.strftime(self.format[1])
