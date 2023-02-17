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

#Instantiate our DAG
etl_dag = DAG( 'dag_scrape_from_wiki',
                default_args=default_arguments,
                description='Extracting World Cup 22 Qatar data' ,
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
    wiki_url = 'https://en.wikipedia.org/wiki/2022_FIFA_World_Cup'  

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

    ### wiki world cup 22 ###
    wiki_dfs = pd.read_html(wiki_url)
    ###################### prize_money ######################## 
    df_prize_money = wiki_dfs[2]
    prize_money_data = {'Place':  df_prize_money['Place']['Place'],
            'Teams': df_prize_money['Teams']['Teams'],
            'amount_per_team_in_millions': df_prize_money['Amount (in millions)']['Per team'],
            'total_amount_in_millions': df_prize_money['Amount (in millions)']['Total'],
            }
    df_prizemoney_cleaned = pd.DataFrame(prize_money_data)

    ###################### bidders ######################## 
    df_bidders = wiki_dfs[3]
    bidders_data = {'Bidders':  df_bidders['Bidders']['Bidders'],
            'Round_1': df_bidders['Votes']['Round 1'],
            'Round_2': df_bidders['Votes']['Round 2'],
            'Round_3': df_bidders['Votes']['Round 3'],
            'Round_4': df_bidders['Votes']['Round 4']
            }

    df_bidders_cleaned = pd.DataFrame(bidders_data)

    ###################### stadiums capacity ######################## 
    df_stadium_capacity = wiki_dfs[4]
    # remove extra characters from Capacity column, convert to float
    df_stadium_capacity['Capacity'] = df_stadium_capacity['Capacity'].str[:6]
    df_stadium_capacity['Capacity'] = df_stadium_capacity['Capacity'].apply(lambda x: x.replace(',', '.'))
    df_stadium_capacity['Capacity'] = df_stadium_capacity['Capacity'].astype('float')

    ###################### Group A ######################## 
    df_group_A = wiki_dfs[9]
    df_group_A.rename(columns = {'Teamvte':'Team','Pld':'Played'}, inplace = True)

    ###################### Group B ######################## 
    df_group_B = wiki_dfs[16]
    df_group_B.rename(columns = {'Teamvte':'Team','Pld':'Played'}, inplace = True)

    ###################### Group C ######################## 
    df_group_C = wiki_dfs[23]
    df_group_C.rename(columns = {'Teamvte':'Team','Pld':'Played'}, inplace = True)

    ###################### Group D ######################## 
    df_group_D = wiki_dfs[30]
    df_group_D.rename(columns = {'Teamvte':'Team','Pld':'Played'}, inplace = True)

    ###################### Group E ######################## 
    df_group_E = wiki_dfs[37]
    df_group_E.rename(columns = {'Teamvte':'Team','Pld':'Played'}, inplace = True)

    ###################### Group F ######################## 
    df_group_F = wiki_dfs[44]
    df_group_F.rename(columns = {'Teamvte':'Team','Pld':'Played'}, inplace = True)

    ###################### Group G ######################## 
    df_group_G = wiki_dfs[51]
    df_group_G.rename(columns = {'Teamvte':'Team','Pld':'Played'}, inplace = True)

    ###################### Group H ######################## 
    df_group_H = wiki_dfs[58]
    df_group_H.rename(columns = {'Teamvte':'Team','Pld':'Played'}, inplace = True)

    ###################### Awards ######################## 
    df_awards = wiki_dfs[83]
    #df_awards = df_awards.head(1)
    awards_table = {'Award_Description': df_awards.columns,
            'Winner': df_awards.iloc[0]
            }

    df_transformed_awards = pd.DataFrame(awards_table)


    ### Connect to Snowflake. Upload data.
    connection = engine.connect()
    #df_market_value.to_sql('player_market_value', con=engine, index=False)
    #df_worldcup_apps.to_sql('world_cup_team_apps', con=engine, index=False)
    #df_manager_appnmtyear.to_sql('manager_appnmt_year', con=engine, index=False)
    #df_manager_origin.to_sql('manager_origin', con=engine, index=False)
    #df_test.to_sql('match_results', con=engine, index=False)
    df_bidders_cleaned.to_sql('bidders', con=engine, index=False) #make sure index is False, Snowflake doesnt accept indexes
    df_prizemoney_cleaned.to_sql('prize_money', con=engine, index=False)
    df_stadium_capacity.to_sql('stadiums', con=engine, index=False)
    df_group_A.to_sql('group_a_standings', con=engine, index=False)
    df_group_B.to_sql('group_b_standings', con=engine, index=False)
    df_group_C.to_sql('group_c_standings', con=engine, index=False)
    df_group_D.to_sql('group_d_standings', con=engine, index=False)
    df_group_E.to_sql('group_e_standings', con=engine, index=False)
    df_group_F.to_sql('group_f_standings', con=engine, index=False)
    df_group_G.to_sql('group_g_standings', con=engine, index=False)
    df_group_H.to_sql('group_h_standings', con=engine, index=False)
    df_transformed_awards.to_sql('awards', con=engine, index=False)
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