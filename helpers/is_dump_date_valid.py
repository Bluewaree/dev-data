from datetime import datetime, timedelta
import sys

sys.path.append('..')
import constants.constants as const

def is_dump_date_valid(dump_date):
    dump_date = datetime.strptime(dump_date, "%Y-%m-%d").date()
    yesterday_date = datetime.today().date() - timedelta(days=1)
    dumps_start_date = datetime.strptime(const.MONGO_DAILY_DUMPS_START_DATE, "%Y-%m-%d").date()
    
    is_monthly_dump_date = dump_date.strftime("%Y-%m-%d") in const.MONGO_MONTHLY_DATES
    is_daily_dump_date = dump_date >= dumps_start_date and dump_date <= yesterday_date

    return is_monthly_dump_date and is_daily_dump_date