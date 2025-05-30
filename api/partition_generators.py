from datetime import datetime
from typing import Iterator

from dateutil.relativedelta import relativedelta


def get_year_month_range(from_date: datetime, to_date: datetime) -> Iterator[str]:
    current = datetime(from_date.year, from_date.month, 1)
    end = datetime(to_date.year, to_date.month, 1)

    while current >= end:
        yield current.strftime("%Y-%m")
        current -= relativedelta(months=1)


def get_year_month_descending(from_date: datetime) -> Iterator[str]:
    i = 0
    while True:
        yield (from_date - relativedelta(months=i)).strftime("%Y-%m")
        i += 1
