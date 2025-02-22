from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def print_hello():
    print("Hello from Airflow!")

def printTen():
    for i in range(1,11):
        print(i)

# Define default_args
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),  # You can define retry delay here
    'start_date': datetime(2024, 12, 9),
}

#A single task (hello_task) within the DAG.
# Define the DAG
with DAG(
    'first_dag',
    default_args=default_args,
    description='this is my first airflow dag',
    schedule_interval=None,  
    catchup=False,
) as dag:
    # Define the Python task
    hello_task = PythonOperator(
        task_id='hello_task',
        python_callable=print_hello,
    )

    ten_task = PythonOperator(
        task_id='ten_task',
        python_callable=printTen,
    )

    hello_task >> ten_task
