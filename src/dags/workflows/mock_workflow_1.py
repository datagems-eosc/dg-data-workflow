# dags/hello_world_dag.py
import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow.providers.standard.operators.empty import EmptyOperator

with DAG(
        dag_id="hello_world",
        start_date=pendulum.datetime(2024, 1, 1),
        schedule=None,
        catchup=False,
        tags=["example", "hello"],
) as dag:
    @task
    def say_hello():
        msg = "Hello, world!"
        print(msg)  # shows that in the task logs
        return msg  # stores that in XCom


    hello = say_hello()

    start = EmptyOperator(task_id="start")

    end = EmptyOperator(task_id="end")

    start >> hello >> end
