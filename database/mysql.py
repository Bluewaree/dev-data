from configparser import ConfigParser
import MySQLdb
import sys
import re
import os

sys.path.append('..')
import constants.constants as const
from helpers.format_string import format_string

config = ConfigParser()
config.read('config.ini')

FOREIGN_KEYS_FILE = config['files']['foreign_keys']
MYSQL_DB = config['mysql']

DATABASE_NAME = MYSQL_DB['name']

class MySQL(object):
    def __init__(self,dump_date = None):

        if dump_date is not None:
            self.db_name = f"{DATABASE_NAME}-{dump_date}"
            print(f"--------------- Connection with db {self.db_name} ------------------")
            self._db = MySQLdb.connect(host = MYSQL_DB['host'],user = MYSQL_DB['user'], passwd = MYSQL_DB['pass'], db = self.db_name, charset="utf8")
        else :
            self._db = MySQLdb.connect(host = MYSQL_DB['host'],user = MYSQL_DB['user'], passwd = MYSQL_DB['pass'], charset="utf8")

    def optimize_load(self):
        cursor = self._db.cursor()
        cursor.execute("set autocommit = 0;set unique_checks = 0;set foreign_key_checks = 0;set sql_log_bin=0;")
        cursor.execute("SET SESSION transaction_isolation='READ-UNCOMMITTED';")
        cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;")
        cursor.close()

    def restore_db(self, csv_file, table_name):
        cursor = self._db.cursor()
        cursor.execute("load data local infile '{0}' \
                        into table {1} \
                        CHARACTER SET UTF8 \
                        fields terminated by ',' \
                        optionally enclosed by '\"' \
                        lines terminated by '\\n'; \
                        ".format(csv_file, table_name))
        cursor.close()

    def restore_users_schema(self, csv_file, table_name):
        cursor = self._db.cursor()
        cursor.execute("load data local infile '{0}' \
                        into table {1} \
                        fields terminated by ',' \
                        optionally enclosed by '\"' \
                        escaped BY '' \
                        lines terminated by '\\n' \
                        ignore 1 lines \
                        (login,@name,@email) SET name=nullif(@name,''),email = nullif(@email,'') \
                        ".format(csv_file, table_name))
        cursor.close()

    def commit(self):
        self._db.commit()

    def update_users(self, users_temp_schema):
        cursor = self._db.cursor()
        cursor.execute(" \
            UPDATE users as u JOIN `{0}`.`users` as u_temp \
            ON u.login = u_temp.login \
            SET u.email = u_temp.email, u.name = u_temp.name; \
        ".format(users_temp_schema))
        cursor.close()

    def execute_file(self,file_to_execute):
        cursor = self._db.cursor()
        cursor.execute(file_to_execute)
        cursor.close()

    def execute_schema_file(self,file_to_execute):
        cursor = self._db.cursor()
        statement = ""
        fk = ""
        fk_file = open(FOREIGN_KEYS_FILE,'w')
        for line in open(file_to_execute):
            if re.search('CREATE TABLE', line.strip("\m")):
                line = line.rstrip('\n')
                table_name = line.split('`')[-2]
                fk = f"alter table {table_name} add "
            if re.match(r'--', line):  # ignore sql comment lines
                continue
            if re.search('CONSTRAINT', line) or re.search('FOREIGN KEY', line):
                line = line.rstrip('\n')
                fk += line
                continue
            if re.search('REFERENCES', line):
                line = f"{line[:-2]};"
                fk += line
                if fk[-1] == ';':
                    fk_file.write(f"{fk}\n")
                else:
                   fk_file.write(f"{fk}")                 
                fk = f"alter table {table_name} add "
                continue
            if re.search('ENGINE',line):
                if statement[-2] == ',':
                    statement = f"{statement[:-2]}){statement[-1]}"
            if not re.search(r';$', line):  # keep appending lines that don't end in ';'
                statement = statement + line
            else:  # when you get a line ending in ';' then exec statement and reset for  next statement
                statement = statement + line
                cursor.execute(statement)
                statement = ""
        fk_file.close()   

    def get_all_users(self):
        cursor = self._db.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT login,name,email FROM users limit 100000")
        users = cursor.fetchall()
        cursor.close()
        return users

    def add_user_name_column(self):
        cursor = self._db.cursor()
        cursor.execute("ALTER TABLE users ADD COLUMN name VARCHAR(255) NULL DEFAULT NULL COMMENT ''")
        cursor.close()

    def add_user_email_column(self):
        cursor = self._db.cursor()
        cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255) NULL DEFAULT NULL COMMENT ''")
        cursor.close()

    def create_index_users_login(self):
        cursor = self._db.cursor()
        cursor.execute("CREATE UNIQUE INDEX `login` ON `users` (`login` ASC)  COMMENT ''")
        cursor.close()

    def drop_database(self,db_name):
        cursor = self._db.cursor()
        cursor.execute("DROP DATABASE `{0}`".format(db_name))
        cursor.close()

    def disconnect(self):
        self._db.close()
