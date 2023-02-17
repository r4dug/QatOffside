import requests
import airflow
import warnings
import time
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
etl_dag = DAG( 'dag_scrape_from_fbref',
                default_args=default_arguments,
                description='Extracting World Cup 22 Qatar data' ,
                schedule_interval = '@weekly',
                tags=['Web Scraping - Players'],
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
    
    warnings.filterwarnings("ignore")

    all_players=[]
    all_keepers=[]

    standing_url="https://fbref.com/en/comps/1/World-Cup-Stats"
    data=requests.get(standing_url)

    league_table=pd.read_html(data.text, match="League Table")[0]

    soup=BeautifulSoup(data.text)

    standing_table=soup.select("table.stats_table")[-1]

    links=standing_table.find_all("a")

    # getting the href attributes on the a tags
    links=[l.get("href") for l in links]

    team_urls=[f"https://fbref.com{l}" for l in links]

    #function for merging multiple datasets
    def merge_mult_dfs(df_list):
        all_merged = df_list[0]
        for to_merge in df_list[1:]:
            all_merged = pd.merge(
                left=all_merged
                ,right=to_merge
                ,how='inner'
                ,on=['Player']
                )
        return all_merged

    # scraping thru for the nation
    #data=requests.get(team_urls[0])

    # Scraping the table needed using read_html
    for team in team_urls:
        team_name=team.split("/")[-1].replace("-Men-Stats","").replace("-"," ")
        data=requests.get(team)
        standard_stats=pd.read_html(data.text,match="Standard Stats")[0]
        standard_stats.columns=standard_stats.columns.droplevel()
        goalkeeping=pd.read_html(data.text, match="Goalkeeping")[0]
        goalkeeping.columns=goalkeeping.columns.droplevel()
        shooting=pd.read_html(data.text, match="Shooting")[0]
        shooting.columns=shooting.columns.droplevel()
        passing=pd.read_html(data.text, match="Passing")[0]
        passing.columns=passing.columns.droplevel()
        pass_types=pd.read_html(data.text, match="Pass Types")[0]
        pass_types.columns=pass_types.columns.droplevel()
        chance_creation=pd.read_html(data.text, match="Goal and Shot Creation")[0]
        chance_creation.columns=chance_creation.columns.droplevel()
        defensive=pd.read_html(data.text, match="Defensive Actions")[0]
        defensive.columns=defensive.columns.droplevel()
        possession=pd.read_html(data.text, match="Possession")[0]
        possession.columns=possession.columns.droplevel()
        playing_time=pd.read_html(data.text, match="Playing Time")[0]
        playing_time.columns=playing_time.columns.droplevel()
        miscellaneous=pd.read_html(data.text, match="Miscellaneous Stats")[0]
        miscellaneous.columns=miscellaneous.columns.droplevel()

        ##### keep the 'standard stats' desired columns
        standard_stats_cols=['Player', 'Pos', 'Age', 'Club', 'MP', 'Starts', 'Min', 'Gls',
            'Ast', 'G-PK', 'PK','CrdY', 'CrdR']
        _stand_stats=standard_stats[standard_stats_cols]

        ##### keep the 'goalkeeping' stats desired columns
        goalkeeping_stats_cols=['Player', 'Pos', 'Age', 'MP', 'Starts', 'Min', 'GA','SoTA', 
        'Saves', 'Save%', 'W', 'D', 'L', 'CS', 'CS%', 'PKatt', 'PKA', 'PKsv', 'PKm']
        _goalkeeping=goalkeeping[goalkeeping_stats_cols]

        ##### keep the 'shooting' stats desired columns
        shooting_stats_cols=['Player','Sh', 'SoT', 'G/Sh', 'FK']
        _shooting=shooting[shooting_stats_cols]

        ##### keep the 'passing' stats desired columns
        passing_stats=passing.iloc[:,4:7]
        passing_stats["Player"]=passing['Player']

        ##### keep the 'shot and chance creation' stats desired columns
        chance_creation_cols = ['Player','SCA']
        _chance_creation = chance_creation[chance_creation_cols]

        ##### keep the 'defensive action' stats desired columns
        defensive_stats_cols=['Player','Tkl', 'TklW','Blocks', 'Int',
            'Tkl+Int', 'Clr', 'Err']
        _defensive=defensive[defensive_stats_cols]

        ##### keep the 'possession' stats desired columns
        possesion_stats_cols=["Player",'Touches', 'Succ%', 'TotDist']
        _possession=possession[possesion_stats_cols]

        ##### keep the 'miscellaneous' stats desired columns
        misc_stats=['Player','Fls', 'Fld',
            'Off', 'Crs', 'Int', 'TklW', 'PKwon', 'PKcon', 'OG', 'Recov','Won',
            'Lost']
        _misc_stats=miscellaneous[misc_stats]

        ##### append all the stats and merge the dfs
        match=[_stand_stats,_shooting,passing_stats,_chance_creation,_defensive,_possession,_misc_stats]
        team_match=merge_mult_dfs(match)

        team_match["Team"]=team_name
        new=team_match.query("Player != 'Squad Total' and Player !='Opponent Total'")

        keepers=_goalkeeping.query("Player != 'Squad Total' and Player !='Opponent Total'")

        all_players.append(new)
        all_keepers.append(keepers)

        time.sleep(3)

    keeper_df=pd.concat(all_keepers)
    match_df=pd.concat(all_players)

    connection = engine.connect()
    #match_df.to_sql('player_stats', con=engine, index=False)
    keeper_df.to_sql('test_rg_fbref_dag', con=engine, index=False)
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