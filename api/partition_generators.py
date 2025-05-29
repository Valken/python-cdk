from datetime import datetime

from dateutil.relativedelta import relativedelta


def get_year_month_range(from_date, to_date):
    current = datetime(from_date.year, from_date.month, 1)
    end = datetime(to_date.year, to_date.month, 1)

    while current >= end:
        yield current.strftime("%Y-%m")
        current -= relativedelta(months=1)


def get_year_month_descending(from_date):
    i = 0
    while True:
        yield (from_date - relativedelta(months=i)).strftime("%Y-%m")
        i += 1
