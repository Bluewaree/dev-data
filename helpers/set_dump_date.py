import os
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

sys.path.append('..')
import constants.constants as const

# Returns the first date if first time run, otherwise returns from last registered date
def set_dump_date(database_type,archives_base_folder,current_dump_date):
    dump_date_file_path = os.path.join(archives_base_folder,f'{database_type}-dump-date.txt')
    
    if database_type==const.MONGO: # Add 1 day if Mongo dump
        next_dump_date = datetime.strptime(current_dump_date, "%Y-%m-%d").date()
    else: # Add 1 month if Mysql dump
        next_dump_date = (datetime.strptime(current_dump_date, "%Y-%m-%d").date()

    with open(dump_date_file_path,"w+") as file:
        file.write(next_dump_date.strftime("%Y-%m-%d"))