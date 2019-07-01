from configparser import ConfigParser
import MySQLdb

config = ConfigParser()
config.read('config.ini')

MYSQL_DB = config['mysql']

DATABASE_NAME = MYSQL_DB['name']

class MySQL(object):
    def __init__(self, db_name = DATABASE_NAME):
        self._db = MySQLdb.connect(host = MYSQL_DB['host'],user = MYSQL_DB['user'], passwd = MYSQL_DB['pass'], db = MYSQL_DB['name'])
    def restoreDB(self, csv_file, table_name):
        cursor = self._db.cursor()
        cursor.execute("load data local infile '~/ghtorrent/{0}' \
                        into table {1} \
                        fields terminated by '|' \
                        enclosed by '\"' \
                        lines terminated by '\\n' \
                        ignore 1 rows \
                        ".format(csv_file, table_name))
