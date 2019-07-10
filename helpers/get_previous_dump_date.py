import os
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

sys.path.append('..')
import constants.constants as const

# Returns the first date if first time run, otherwise returns from last registered date
def get_previous_dump_date(database_type,archives_base_folder):
    dump_date = const.DUMPS_START_DATE[database_type]
    dump_date_file_path = os.path.join(archives_base_folder,f'{database_type}-dump-date.txt')

    if os.path.exists(dump_date_file_path): 
        with open(dump_date_file_path) as file:
            dump_date = file.readline()
    
    if database_type==const.MONGO: # Yesterday if mongo
        previous_dump_date = datetime.strptime(dump_date, "%Y-%m-%d").date() - relativedelta(days=1)
    else: # Last month if mysql
        previous_dump_date = (datetime.strptime(dump_date, "%Y-%m-%d").date() - relativedelta(months=1)).replace(day=1)

    return dump_date