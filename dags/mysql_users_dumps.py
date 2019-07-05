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
from helpers.get_mysql_table_names import get_mysql_table_names

# importing mongo class for db management
from database.mysql import MySQL

config = ConfigParser()
config.read('config.ini')

ARCHIVES_BASE_FOLDER = config['archives']['ghtorrent']
MYSQL = const.MYSQL
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
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
}

# Defining DAG
dag = DAG('mysql_users_dump', default_args=default_args, schedule_interval='@monthly',max_active_runs=1)

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

def restore_dump_process():
    dump_date = get_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    mysql = MySQL(dump_date)
    mysql_tables = get_mysql_table_names(os.path.join(get_dump_folder_path(ARCHIVES_BASE_FOLDER,MYSQL,dump_date),'dump'))
    mysql.optimize_load()
    for mysql_table in mysql_tables:
        print(f'-------------- Processing {mysql_table} ----------------')
        csv_file = os.path.join(get_dump_folder_path(ARCHIVES_BASE_FOLDER,MYSQL,dump_date),'dump','{0}.csv'.format(mysql_table))
        mysql.restore_db(csv_file,mysql_table)
        print(f'-------------- Processing ended ----------------')
    print("----------------- Committing -----------------")
    mysql.commit()

def set_next_dump_date_process():
    dump_date = get_dump_date(MYSQL,ARCHIVES_BASE_FOLDER)
    set_dump_date(MYSQL,ARCHIVES_BASE_FOLDER,dump_date)


# ------------- Defining Tasks -------------
download_dump_task = PythonOperator(task_id='download-dump', python_callable=download_dump_process, dag=dag)
extract_file_task = PythonOperator(task_id='extract-file', python_callable=extract_file_process, dag=dag)
restore_dump_task = PythonOperator(task_id='restore-dump', python_callable=restore_dump_process, dag=dag)
set_next_dump_date_task = PythonOperator(task_id='set-next-dump-date', python_callable=set_next_dump_date_process, dag=dag)

download_dump_task >> extract_file_task >> restore_dump_task >> set_next_dump_date_task
