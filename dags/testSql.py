from airflow import DAG
from airflow.operators.mysql_operator import MySqlOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2022, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'example_mysql_dag',
    default_args=default_args,
    schedule_interval=timedelta(days=1),
)

with dag:
    insert_task = MySqlOperator(
        task_id='insert_data_task',
        mysql_conn_id='aflw',  # Use the connection id you created
        sql="""
        INSERT INTO scrapy_afw.web_scrap (uid, att, nos)
        VALUES
            (7, 'Attribute4', 'Number4'),
            (8, 'Attribute5', 'Number5'),
            (9, 'Attribute6', 'Number6');
        """,
    )

