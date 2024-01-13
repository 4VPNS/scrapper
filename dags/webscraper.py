from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import requests
from bs4 import BeautifulSoup
import re
import csv
from time import sleep
import pandas as pd
import ast



def extract_data():
    ticker_symbol = 'SBIN'
    url = f'https://www.screener.in/company/{ticker_symbol}/'
    res = requests.get(url)
    # soup = BeautifulSoup(res.text, 'html.parser')
    return res.text

def transform_data(html_text, **kwargs):
    # Transformation logic (modify as needed)
    soup = BeautifulSoup(html_text, 'html.parser')
    nos = [element.text.strip() for element in soup.find_all("span", class_="number")]
    atts = [element.text.strip() for element in soup.find_all("span", class_="name")]
    final={}
    for i in range(len(atts)):

        if i>2:
            final[atts[i]]=nos[i+1]
        else:
            final[atts[i]]=nos[i]
        
    return final


def load_data(**context):
    final = context['task_instance'].xcom_pull(task_ids='transform_data')
    if isinstance(final, str):
        final = ast.literal_eval(final)  # Convert string to dictionary only if final is a string
    df = pd.DataFrame(list(final.items()), columns=['Attribute', 'Value'])
    df.to_csv('your_filename.csv', index=False)
    # Rest of your loading logic
    return 'Successfully saved to CSV'


default_args = {
    'owner': 'navanish',
    'start_date': datetime(2024, 1, 13),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'etl_dag',
    default_args=default_args,
    description='ETL DAG for web scraping',
    schedule_interval=timedelta(days=1),
)

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    provide_context=True,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    op_args=['{{ ti.xcom_pull(task_ids="extract_data") }}'],
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    provide_context=True,
    dag=dag,
)

extract_task >> transform_task >> load_task