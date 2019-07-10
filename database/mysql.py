from configparser import ConfigParser
import MySQLdb
import sys

sys.path.append('..')
import constants.constants as const
from helpers.format_string import format_string

config = ConfigParser()
config.read('config.ini')

MYSQL_DB = config['mysql']

DATABASE_NAME = MYSQL_DB['name']

class MySQL(object):
    def __init__(self,dump_date = None):

        if dump_date is not None:
            db_name = f"{DATABASE_NAME}-{dump_date}"
            print(f"--------------- Connection with db {db_name} ------------------")
            self._db = MySQLdb.connect(host = MYSQL_DB['host'],user = MYSQL_DB['user'], passwd = MYSQL_DB['pass'], db = db_name)
        else :
            self._db = MySQLdb.connect(host = MYSQL_DB['host'],user = MYSQL_DB['user'], passwd = MYSQL_DB['pass'])

    def optimize_load(self):
        cursor = self._db.cursor()
        cursor.execute("set autocommit = 0;set unique_checks = 0;set foreign_key_checks = 0;set sql_log_bin=0;")
        cursor.close() 

    def restore_db(self, csv_file, table_name):
        cursor = self._db.cursor()
        cursor.execute("SELECT @@foreign_key_checks;")
        print(cursor.fetchone())
        cursor.execute("load data local infile '{0}' \
                        into table {1} \
                        fields terminated by ',' \
                        enclosed by '\"' \
                        lines terminated by '\\n'; \
                        ".format(csv_file, table_name))
        cursor.close() 

    def commit(self):
        self._db.commit()

    def update_users(self, users, database_documents_type):
        cursor = self._db.cursor()
        cursor.execute("SET GLOBAL range_optimizer_max_mem_size=0;")
        cursor.execute("show variables like \"range_optimizer_max_mem_size\"")
        print(cursor.fetchone())
        query = ""
        email_case = "email = case"
        name_case = "name = case"
        logins = []
        for user in users:
            if database_documents_type == const.MONGO:
                user = user['data']
            login = format_string(user['login'])
            email = format_string(user['email'])
            name = format_string(user['name'])
            email_case += f" when login = %s then %s" % (login,email)
            name_case += f" when login = %s then %s" % (login,name)
            logins.append(login)
        email_case += " else email end"
        name_case += " else name end"
        logins = ','.join(logins)
        query = f"update users set {email_case}, {name_case} where login in ({logins})"
        print("---- Query Ready ------")
        cursor.execute(query)
        print("---- Query ended -----")
        cursor.close() 
        
    def execute_file(self,file_to_execute):
        cursor = self._db.cursor()
        cursor.execute(file_to_execute)
        cursor.close() 

    def get_all_users(self):
        cursor = self._db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT login,name,email FROM users limit 100000")
        users = cursor.fetchall()
        cursor.close()
        return users