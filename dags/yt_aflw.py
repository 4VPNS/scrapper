from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.providers.mysql.hooks.mysql import MySqlHook
from googleapiclient.discovery import build
import pandas as pd

api_key = 'Your API key'
youtube = build('youtube', 'v3', developerKey=api_key)

def comments_load(**kwargs):
    video_url = 'https://www.youtube.com/watch?v=TRPjd6W71JE'
    video_id = video_url.split('v=')[1]
    comments = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText'
    ).execute()

    comment_list = []
    for comment in comments['items']:
        author = comment['snippet']['topLevelComment']['snippet']['authorDisplayName']
        text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
        comment_list.append({'authors': author, 'comments': text})
    return comment_list

def load_data(**context):
    comment_list = context['task_instance'].xcom_pull(task_ids='comments_task')
    df = pd.DataFrame(comment_list)
    df.insert(0, 'uid', range(1, 1 + len(df)))
    data_tuples = list(df.itertuples(index=False, name=None))
    return data_tuples

class MySqlInsertOperator(BaseOperator):
    @apply_defaults
    def __init__(self, mysql_conn_id, sql, xcom_task_id=None, *args, **kwargs):
        super(MySqlInsertOperator, self).__init__(*args, **kwargs)
        self.mysql_conn_id = mysql_conn_id
        self.sql = sql
        self.xcom_task_id = xcom_task_id

    def execute(self, context):
        data_tuples = context['task_instance'].xcom_pull(task_ids=self.xcom_task_id)
        mysql_hook = MySqlHook(mysql_conn_id=self.mysql_conn_id)
        for data in data_tuples:
            print("Current data:", data)
            params = (data[0], data[1], data[2])
            mysql_hook.run(self.sql, parameters=params)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 19),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'yt_dag',
    default_args=default_args,
    description='ETL DAG for yotube data',
    schedule_interval=timedelta(days=1),
)

commentsTask = PythonOperator(
    task_id='comments_task',
    python_callable=comments_load,
    do_xcom_push=True,
    dag=dag,
)

loadDataTask = PythonOperator(
    task_id='load_data_task',
    python_callable=load_data,
    provide_context=True,
    dag=dag,
)

insert_task = MySqlInsertOperator(
    task_id='insert_data_task',
    mysql_conn_id='aflw',
    sql="INSERT INTO scrapy_afw.yt_comments (uid, authors, comments) VALUES (%s, %s, %s)",
    xcom_task_id='load_data_task',
    dag=dag
)

commentsTask >> loadDataTask >> insert_task