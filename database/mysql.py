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
        cursor.execute("set autocommit = 0;set unique_checks = 0;set foreign_key_checks = 0;set sql_log_bin=0;")
        cursor.execute("load data local infile '~/{0}' \
                        into table {1} \
                        fields terminated by ',' \
                        enclosed by '\"' \
                        lines terminated by '\\n' \
                        ignore 1 rows \
                        ".format(csv_file, table_name))
    def update_users(self, users):
        cursor = self._db.cursor()
        query = ""
        email_case = "email = case"
        name_case = "name = case"
        logins = []
        for user in users:
            user = user['data']
            email_case += f" when login = {user['login']} then {user['email']}"
            name_case += f" when login = {user['login']} then {user['name']}"
            logins.append(user['login'])
        email_case += " else email end"
        name_case += " else name end"
        logins = ','.join(logins)
        query = f"update users set {email_case}, {name_case} where login in ({logins})"
        cursor.execute(query)
