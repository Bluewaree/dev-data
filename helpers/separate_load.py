from multiprocessing import Pool
import MySQLdb
from configparser import ConfigParser

import sys
sys.path.append('..')

from database.mysql import MySQL

config = ConfigParser()
config.read('config.ini')

MYSQL_DB = config['mysql']

def process(table):
    global dump_date
    global file_destination

    mysql = MySQL(dump_date)
    mysql.optimize_load()
    print(f"processing table {table}")
    csv_file = f"{file_destination}/{table}.csv"
    mysql.restore_db(csv_file,table)
    print(f"finished processing file {table}")
    mysql.commit()
    mysql.disconnect()


def separate_load(date, destination, tables):
    global dump_date
    global file_destination

    dump_date = date
    file_destination = destination
    with Pool(12) as pool:
         pool.map(process, tables)
         pool.close()
         pool.join()