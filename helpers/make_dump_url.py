from datetime import datetime, timedelta
import sys

sys.path.append('..')
import constants.constants as const

def make_dump_url(dump_date,database_type,mongo_collection=None):
    if database_type == const.MYSQL:
        return f'{const.MYSQL_MONTHLY_DUMPS_URL}{dump_date}.tar.gz'

    if database_type == const.MONGO and dump_date in const.MONGO_MONTHLY_DATES:
        return f'{const.MONGO_MONTHLY_DUMPS_URLS}{mongo_collection}-dump.{dump_date}.tar.gz'
    else:
        return f'{const.MONGO_DAILY_DUMPS_URL}{dump_date}.tar.gz'