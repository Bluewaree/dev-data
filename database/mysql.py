from configparser import ConfigParser
import MySQLdb

config = ConfigParser()
config.read('config.ini')

MYSQL_DB = config['mysql']

DATABASE_NAME = MYSQL_DB['name']

class MySQL(object):
    def __init__(self,dump_date,db_name = DATABASE_NAME):
        db_name += f"-{dump_date}"
        self._db = MySQLdb.connect(host = MYSQL_DB['host'],user = MYSQL_DB['user'], passwd = MYSQL_DB['pass'], db = db_name)
    def restore_db(self, csv_file, table_name):
        cursor = self._db.cursor()
        cursor.execute("set autocommit = 0;set unique_checks = 0;set foreign_key_checks = 0;set sql_log_bin=0;")
        cursor.execute("load data local infile '{0}' \
                        into table {1} \
                        fields terminated by ',' \
                        enclosed by '\"' \
                        lines terminated by '\\n'; \
                        ".format(csv_file, table_name))
    def commit(self):
        self._db.commit()
