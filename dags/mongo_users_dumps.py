from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from configparser import ConfigParser

import os
import sys
from pathlib import Path
home = str(Path.home())
sys.path.append(home)

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
from helpers.get_previous_dump_date import get_previous_dump_date
from helpers.get_dump_folder_endpoint import get_dump_folder_endpoint

# importing mongo class for db management
from database.mongodb import MongoDB
from database.mysql import MySQL

config = ConfigParser()
config.read('config.ini')

ARCHIVES_BASE_FOLDER = config['archives']['ghtorrent']
MONGO = const.MONGO
MYSQL = const.MYSQL
MONGO_DUMPS_START_DATE = const.DUMPS_START_DATE[MONGO]
USERS_SCHEMA = const.MONGO_USERS_GITHUB_SCHEMA
USERS= const.USERS
USERS_TEMP= const.USERS_TEMP
SCHEMA = const.SCHEMA

# Defining DAG's default args
default_args = {
    'owner': 'airflow',
    'wait_for_downstream': True,
    'depends_on_past': True,
    'start_date': datetime.strptime(MONGO_DUMPS_START_DATE, "%Y-%m-%d"),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
}

# Defining DAG
dag = DAG('mongo_users_dump', default_args=default_args, schedule_interval=timedelta(days=1),max_active_runs=1) 

def download_dump_process():
    dump_date = get_dump_date(MONGO,ARCHIVES_BASE_FOLDER)
    if is_dump_date_valid(dump_date):
        url = make_dump_url(dump_date,MONGO,USERS)
        destination_path = get_dump_archive_file_path(ARCHIVES_BASE_FOLDER,MONGO,dump_date)
        download_dump(url,destination_path)

def extract_file_process():
    dump_date = get_dump_date(MONGO,ARCHIVES_BASE_FOLDER)
    if is_dump_date_valid(dump_date):
        destination_path = get_dump_folder_path(ARCHIVES_BASE_FOLDER,MONGO,dump_date)
        create_folder(destination_path)
        dump_file_to_extract = get_dump_archive_file_path(ARCHIVES_BASE_FOLDER,MONGO,dump_date)
        extract_file(dump_file_to_extract,destination_path)

def restore_dump_process():
    dump_date = get_dump_date(MONGO,ARCHIVES_BASE_FOLDER)
    if is_dump_date_valid(dump_date):
        mongodb = MongoDB()
        bson_file = os.path.join(get_dump_folder_endpoint(ARCHIVES_BASE_FOLDER,MONGO,dump_date),f'{USERS}.bson')
        mongodb.restore_db(bson_file,USERS_SCHEMA)

def remove_duplicates_process():
    dump_date = get_dump_date(MONGO,ARCHIVES_BASE_FOLDER)
    if is_dump_date_valid(dump_date):
        mongodb = MongoDB()
        mongodb.connect()
        mongodb.remove_duplicates()
        mongodb.disconnect()

def remove_documents_with_null_values_process():
    dump_date = get_dump_date(MONGO,ARCHIVES_BASE_FOLDER)
    if is_dump_date_valid(dump_date):
        mongodb = MongoDB()
        mongodb.connect()
        mongodb.remove_documents_with_null_values()
        mongodb.disconnect()

def export_users_schema_process():
    dump_date = get_dump_date(MONGO,ARCHIVES_BASE_FOLDER)
    if is_dump_date_valid(dump_date):        
        export_destinqtion = os.path.join(ARCHIVES_BASE_FOLDER,f"{MONGO}-{USERS}-{dump_date}.csv")
        mongodb = MongoDB()
        mongodb.export_users_schema(export_destinqtion,USERS_SCHEMA)

def create_mysql_schema_process():
    dump_date = get_dump_date(MONGO,ARCHIVES_BASE_FOLDER)
    if is_dump_date_valid(dump_date):
        schema_file = f'/{USERS_TEMP}-{SCHEMA}.sql'
        schema_file = open(schema_file, 'r').read()
        mysql = MySQL()
        mysql.execute_file(schema_file)
        mysql.disconnect()

def update_mysql_process():
    dump_date = get_dump_date(MONGO,ARCHIVES_BASE_FOLDER)
    if is_dump_date_valid(dump_date):
        mongodb = MongoDB()
        mongodb.connect()
        users = mongodb.retrieve_users()
        previous_mysql_dump_date = get_previous_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
        mysql = MySQL(previous_mysql_dump_date)
        mysql.update_users(users,MONGO)

def remove_dump_process():
    dump_date = get_dump_date(MONGO,ARCHIVES_BASE_FOLDER)
    if is_dump_date_valid(dump_date): 
        dump_folder = get_dump_folder_path(ARCHIVES_BASE_FOLDER,MONGO,dump_date)
        dump_file = get_dump_archive_file_path(ARCHIVES_BASE_FOLDER,MONGO,dump_date)
        remove_dump(dump_file,dump_folder)

def drop_database_process():
    dump_date = get_dump_date(MONGO,ARCHIVES_BASE_FOLDER)
    if is_dump_date_valid(dump_date): 
        mongodb = MongoDB()
        MongoDB.drop_database()

def set_next_dump_date_process():
    dump_date = get_dump_date(MONGO,ARCHIVES_BASE_FOLDER)
    set_dump_date(MONGO,ARCHIVES_BASE_FOLDER,dump_date)
        

# ------------- Defining Tasks ------------- 
download_dump_task = PythonOperator(task_id='download-dump', python_callable=download_dump_process, dag=dag)
extract_file_task = PythonOperator(task_id='extract-file', python_callable=extract_file_process, dag=dag)
restore_dump_task = PythonOperator(task_id='restore-dump', python_callable=restore_dump_process, dag=dag)
remove_duplicates_task = PythonOperator(task_id='remove-duplicates', python_callable=remove_duplicates_process, dag=dag)
remove_documents_with_null_values_task = PythonOperator(task_id='remove-documents-with-null-values', python_callable=remove_documents_with_null_values_process, dag=dag)
export_users_schema_task = PythonOperator(task_id='export-users-schema', python_callable=export_users_schema_process, dag=dag)
create_mysql_schema_task = PythonOperator(task_id='create-mysql-schema', python_callable=create_mysql_schema_process, dag=dag)
update_mysql_task = PythonOperator(task_id='update-mysql', python_callable=update_mysql_process, dag=dag)
remove_dump_task = PythonOperator(task_id='remove-dump', python_callable=remove_dump_process, dag=dag)
drop_database_task = PythonOperator(task_id='drop-database', python_callable=drop_database_process, dag=dag)
set_next_dump_date_task = PythonOperator(task_id='set-next-dump-date', python_callable=set_next_dump_date_process, dag=dag)

download_dump_task >> extract_file_task >> restore_dump_task >> remove_duplicates_task >> remove_documents_with_null_values_task >> export_users_schema_task >> create_mysql_schema_task >> update_mysql_task >> remove_dump_task >> drop_database_task >> set_next_dump_date_task