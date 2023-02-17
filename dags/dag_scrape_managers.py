import requests
import airflow
from airflow.models import DAG 
from airflow.operators.python import PythonOperator
from datetime import timedelta 
import pandas as pd
import snowflake.connector as snow_conn
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from bs4 import BeautifulSoup

default_arguments = { 'owner': 'test',
                        'email': 'test@test.com',
                        'email_on_failure': False,   
                        'email_on_success': False,
                        'start_date': airflow.utils.dates.days_ago(0),
                        'retries':1 ,
                        'retry_delay':timedelta(minutes=5)}  

#Instantiate our DAG
etl_dag = DAG( 'dag_scrape_managers',
                default_args=default_arguments,
                description='Extracting World Cup 22 Qatar data' ,
                schedule_interval = '@weekly',
                tags=['Web Scraping - Managers'],
                 )

engine=create_engine(URL(
    user='adinai',
    password='WorldCup22',
    account='jnsqfyg-yu12859',
    warehouse='COMPUTE_WH',
    database='QAT_OFFSIDE',
    schema='public',
    role='ACCOUNTADMIN'
    ))

def validation_connection(conn, **kwargs):
    ctx = snow_conn.connect(
    user='adinai',
    password='WorldCup22',
    account='jnsqfyg-yu12859',
    database = 'QAT_OFFSIDE',
    warehouse = 'COMPUTE_WH',
    schema = 'public'
    )
    cs = ctx.cursor()
    try:
        cs.execute("SELECT current_version()")
        one_row = cs.fetchone()
        print(one_row[0])
        print("Successfully connected to Snowflake Database")
    finally:
        cs.close()
    ctx.close()
    
# Data Processing Function 
def extract_data_send_to_snowflake():
    # Request the website
    url = "https://www.sportingnews.com/us/soccer/news/world-cup-oldest-youngest-coach-manager-qatar-2022/p7lpiwcqesfxdbzfiqwofne0"
    response = requests.get(url)

    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the tables in the HTML
    tables = soup.find_all('table')

    # Create a list to store the dataframes
    dataframes = []

    # Iterate through the tables and extract the data
    for table in tables:
        df_managers = pd.read_html(str(table))[0]
        dataframes.append(df_managers)

    connection = engine.connect()
    df_managers.to_sql('manager_age', con=engine, index=False)
    connection.close()
    engine.dispose()

# Conection Task
validation = PythonOperator(task_id='CONNECTION_SUCCESS', 
                            provide_context=True,    
                            python_callable=validation_connection,
                            op_kwargs={"conn":engine},     
                            dag=etl_dag )

# Data Extraction, Processing, Sending to Snowflake Warehouse
extract_send = PythonOperator(task_id='EXTRACTING_DATA',     
                             python_callable=extract_data_send_to_snowflake,     
                             dag=etl_dag )

validation >> extract_send