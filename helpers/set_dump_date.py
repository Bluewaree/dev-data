import os
import sys
from datetime import datetime, timedelta

# Returns the first date if first time run, otherwise returns from last registered date
def set_dump_date(database_type,archives_base_folder,current_dump_date):
    dump_date_file_path = os.path.join(archives_base_folder,f'{database_type}-dump-date.txt')

    with open(dump_date_file_path,"w+") as file:
        next_dump_date = datetime.strptime(current_dump_date, "%Y-%m-%d").date() + timedelta(days=1)
        file.write(next_dump_date.strftime("%Y-%m-%d"))