from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from configparser import ConfigParser
import os

# importing constants
import constants.constants as const

# importing helpers
from helpers.get_dump_date import get_dump_date
from helpers.is_dump_date_valid import is_dump_date_valid
from helpers.make_dump_url import make_dump_url
from helpers.download_dump import download_dump
from helpers.create_folder import create_folder
from helpers.extract_file import extract_file
from helpers.set_dump_date import set_dump_date
from helpers.remove_dump import remove_dump
from helpers.get_dump_archive_file_path import get_dump_archive_file_path
from helpers.get_dump_folder_path import get_dump_folder_path
from helpers.get_mysql_table_names import get_mysql_table_names
from helpers.separate_restoration_mysql import separate_restoration
from helpers.change_content_in_file import change_content_in_file
from helpers.copy_file import copy_file
from helpers.get_dump_folder_endpoint import get_dump_folder_endpoint
from helpers.get_previous_dump_date import get_previous_dump_date
from helpers.separate_load import separate_load

# importing mongo class for db management
from database.mysql import MySQL

config = ConfigParser()
config.read('config.ini')

FOREIGN_KEYS_FILE = config['files']['foreign_keys']
SCHEMA_FILE = config['files']['schema']
INDEXES_FILE = config['files']['indexes']
ARCHIVES_BASE_FOLDER = const.GHTORRENT
GHTORRENT = const.GHTORRENT
MYSQL = const.MYSQL
SCHEMA = const.SCHEMA
INDEXES = const.INDEXES
MYSQL_DUMPS_START_DATE = const.DUMPS_START_DATE[MYSQL]

# Defining DAG's default args
default_args = {
    'owner': 'airflow',
    'wait_for_downstream': True,
    'depends_on_past': True,
    'start_date': datetime.strptime(MYSQL_DUMPS_START_DATE, "%Y-%m-%d"),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
}

# Defining DAG
dag = DAG('mysql_users_dump', default_args=default_args, schedule_interval='@once',max_active_runs=1)

def download_dump_process():
    dump_date = get_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    url = make_dump_url(dump_date,MYSQL)
    destination_path = get_dump_archive_file_path(ARCHIVES_BASE_FOLDER,MYSQL,dump_date)
    download_dump(url,destination_path)

def extract_file_process():
    dump_date = get_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    destination_path = get_dump_folder_path(ARCHIVES_BASE_FOLDER,MYSQL,dump_date)
    create_folder(destination_path)
    dump_file_to_extract = get_dump_archive_file_path(ARCHIVES_BASE_FOLDER,MYSQL,dump_date)
    extract_file(dump_file_to_extract,destination_path)

def create_schema_process():
    dump_date = get_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    dump_schema_file = os.path.join(get_dump_folder_endpoint(ARCHIVES_BASE_FOLDER,MYSQL,dump_date),f'{SCHEMA}.sql')
    change_content_in_file(GHTORRENT,f"{GHTORRENT}-{dump_date}",dump_schema_file)
    copy_file(dump_schema_file,SCHEMA_FILE)
    change_content_in_file(f"{GHTORRENT}-{dump_date}",GHTORRENT,dump_schema_file)
    mysql = MySQL()
    mysql.execute_schema_file(SCHEMA_FILE)
    mysql.add_user_name_column()
    mysql.add_user_email_column()
    mysql.disconnect()

def restore_dump_process():
    dump_date = get_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    mysql_tables = get_mysql_table_names(os.path.join(get_dump_folder_endpoint(ARCHIVES_BASE_FOLDER,MYSQL,dump_date)))
    dump_folder_endpoint = get_dump_folder_endpoint(ARCHIVES_BASE_FOLDER,MYSQL,dump_date)
    separate_load(dump_date,dump_folder_endpoint,mysql_tables)

def add_foreign_keys_process():   
    dump_date = get_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    mysql = MySQL(dump_date)
    mysql.optimize_load()
    foreign_key_file = open(FOREIGN_KEYS_FILE, 'r').read()
    mysql.execute_file(foreign_key_file)
    mysql.disconnect()

def create_indexes_process():
    dump_date = get_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    dump_indexes_file = os.path.join(get_dump_folder_endpoint(ARCHIVES_BASE_FOLDER,MYSQL,dump_date),f'{INDEXES}.sql')
    change_content_in_file(GHTORRENT,f"{GHTORRENT}-{dump_date}",dump_indexes_file)
    copy_file(dump_indexes_file,INDEXES_FILE)
    change_content_in_file(f"{GHTORRENT}-{dump_date}",GHTORRENT,dump_indexes_file)
    indexes_files = open(INDEXES_FILE, 'r').read()
    mysql = MySQL(dump_date)
    mysql.execute_file(indexes_files)
    mysql.disconnect()

def restore_old_users_data_process():
    dump_date = get_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    previous_mysql_dump_date = get_previous_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    db_name = f"{GHTORRENT}-{previous_mysql_dump_date}"
    if dump_date != previous_mysql_dump_date:
        mysql = MySQL(f"{dump_date}")
        mysql.update_users(db_name)
        mysql.commit()
        mysql.disconnect()

def drop_old_database_process():
    dump_date = get_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    previous_mysql_dump_date = get_previous_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    if dump_date != previous_mysql_dump_date:
        mysql = MySQL()
        db_name = f"{GHTORRENT}-{previous_mysql_dump_date}"
        mysql.drop_database(db_name)
        mysql.disconnect()

def set_next_dump_date_process():
    dump_date = get_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    set_dump_date(MYSQL,ARCHIVES_BASE_FOLDER,dump_date)


# ------------- Defining Tasks -------------
download_dump_task = PythonOperator(task_id='download-dump', python_callable=download_dump_process, dag=dag)
extract_file_task = PythonOperator(task_id='extract-file', python_callable=extract_file_process, dag=dag)
create_schema_task = PythonOperator(task_id='create-schema', python_callable=create_schema_process, dag=dag)
restore_dump_task = PythonOperator(task_id='restore-dump', python_callable=restore_dump_process, dag=dag)
add_foreign_keys_task = PythonOperator(task_id='add-foreign-keys', python_callable=add_foreign_keys_process, dag=dag, trigger_rule='all_done')
create_indexes_task = PythonOperator(task_id='create-indexes', python_callable=create_indexes_process, dag=dag, trigger_rule='all_done')
restore_old_users_data_task = PythonOperator(task_id='resrtore-old-users-data', python_callable=restore_old_users_data_process, dag=dag, trigger_rule='all_done')
drop_old_database_task = PythonOperator(task_id='drop-old-database', python_callable=drop_old_database_process, dag=dag)
set_next_dump_date_task = PythonOperator(task_id='set-next-dump-date', python_callable=set_next_dump_date_process, dag=dag)

download_dump_task >> extract_file_task >> create_schema_task >> restore_dump_task >> add_foreign_keys_task >> create_indexes_task >> restore_old_users_data_task >> drop_old_database_task >> set_next_dump_date_task
