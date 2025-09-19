from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG(
    dag_id="123456",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False
) as dag:
    
    start = EmptyOperator(task_id="start")
    task = EmptyOperator(task_id="dag_one")
    end = EmptyOperator(task_id="end")

    start >> task >> end
