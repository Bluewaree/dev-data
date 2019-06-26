from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

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

ARCHIVES_BASE_FOLDER = config['archives']['ghtorrent']
MONGO = const.MONGO
MONGO_DUMPS_START_DATE = consot.DUMPS_START_DATE[MONGO]

# Defining DAG's default args
default_args = {
    'owner': 'airflow',
    'depends_on_past': True,
    'start_date': datetime.strptime(MONGO_DUMPS_START_DATE, "%Y-%m-%d"),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
}

# Defining DAG
dag = DAG('mongo_users_dump', default_args=default_args, schedule_interval=timedelta(days=1))

def download_dump_process():
    dump_date = get_dump_date(MONGO)
    if is_dump_date_valid(dump_date):
        url = make_dump_url(dump_date,MONGO,'users')
        destination_path = os.path.join(ARCHIVES_BASE_FOLDER,f'mongo-dump-{dump_date}.tar.gz')
        download_dump(url,destination_path)

# ------------- Defining Tasks ------------- 
download_dump_task = PythonOperator(task_id='download-dump', python_callable=download_dump_process, dag=dag)