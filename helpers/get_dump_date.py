import os
import sys

sys.path.append('..')
import constants.constants as const

# Returns the first date if first time run, otherwise returns from last registered date
def get_dump_date(database_type,archives_base_folder):
    dump_date = const.DUMPS_START_DATE[database_type]
    dump_date_file_path = os.path.join(archives_base_folder,f'{database_type}-dump-date.txt')

    if os.path.exists(dump_date_file_path): 
        with open(dump_date_file_path) as file:
            dump_date = file.readline()
    return dump_date