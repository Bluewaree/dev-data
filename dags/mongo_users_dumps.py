from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

import sys
from pathlib import Path
home = str(Path.home())
sys.path.append(home)

# importing constants and helpers
import constants.constants as const
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