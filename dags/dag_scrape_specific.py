import requests
import airflow
from airflow.models import DAG 
from airflow.operators.python import PythonOperator
from datetime import timedelta 
import pandas as pd
import snowflake.connector as snow_conn
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

default_arguments = { 'owner': 'test',
                        'email': 'test@test.com',
                        'email_on_failure': False,   
                        'email_on_success': False,
                        'start_date': airflow.utils.dates.days_ago(0),
                        'retries':1 ,
                        'retry_delay':timedelta(minutes=5)}  

# Instanciamos nuestro DAG 
etl_dag = DAG( 'abcde',
                default_args=default_arguments,
                description='Extracting World Cup data' ,
                schedule_interval = '@weekly',
                tags=['Web Scraping'],
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
    ### urls ###
    market_value_url = 'https://bolavip.com/en/qatar2022/qatar-2022-list-of-50-world-cup-players-with-the-highest-market-value-20221117-0021.html'
    no_world_cup_apps_url = 'https://en.wikipedia.org/wiki/National_team_appearances_in_the_FIFA_World_Cup'
    manager_appnmtyear_url = 'https://worldsoccertalk.com/news/foreign-born-managers-seek-rare-successes-at-world-cup-2022-20220802-CMS-394875.html'
    manager_origin_url = 'https://footballnewzz.com/world-cup-coaches-2022-qatar/'
    saudi_arabia_manager_url = 'https://en.wikipedia.org/wiki/Herv%C3%A9_Renard'
    results_url = requests.get('https://terrikon.com/en/worldcup-2022')   

    ### market value ###
    mv_list = pd.read_html(market_value_url)
    df_market_value = mv_list[0]
    df_market_value = df_market_value.rename(columns={1: 'Player', 2: 'Age', 3:'Team', 4:'Market_value'}).drop(0,axis=1).iloc[1:] 

    ### no of world cup apps ###
    wiki_worldcup_apps_list = pd.read_html(no_world_cup_apps_url)
    df_worldcup_apps = wiki_worldcup_apps_list[0]

    ### manager appointment year ###
    manager_appnmtyear_list = pd.read_html(manager_appnmtyear_url)
    df_manager_appnmtyear = manager_appnmtyear_list[0]

    ### manager origin ###
    manager_origin_list = pd.read_html(manager_origin_url)
    df_manager_origin = manager_origin_list[0]

    ### managerial career ###
    wiki = pd.read_html(saudi_arabia_manager_url)
    df_rwar = wiki[1]

    ### match results ###
    results = pd.read_html(results_url.text)
    df_test = results[1]
    df_test = df_test.rename(columns={1: 'Team1', 2: 'Score', 3:'Team2', 5:'Date'}).drop([0,4],axis=1)

    ### Connect to Snowflake. Upload data.
    connection = engine.connect()
    #df_market_value.to_sql('player_market_value', con=engine, index=False)
    #df_worldcup_apps.to_sql('world_cup_team_apps', con=engine, index=False)
    #df_manager_appnmtyear.to_sql('manager_appnmt_year', con=engine, index=False)
    #df_manager_origin.to_sql('manager_origin', con=engine, index=False)
    #df_test.to_sql('match_results', con=engine, index=False)
    df_test.to_sql('match_results', con=engine, index=False)
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