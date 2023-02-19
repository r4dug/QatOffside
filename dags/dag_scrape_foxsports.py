import requests
import airflow
from airflow.models import DAG 
from airflow.operators.python import PythonOperator
from datetime import timedelta 
import pandas as pd
import snowflake.connector as snow_conn
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
import urllib.request
from html_table_parser.parser import HTMLTableParser

default_arguments = { 'owner': 'test',
                        'email': 'test@test.com',
                        'email_on_failure': False,   
                        'email_on_success': False,
                        'start_date': airflow.utils.dates.days_ago(0),
                        'retries':1 ,
                        'retry_delay':timedelta(minutes=5)}  

#Instantiate our DAG
etl_dag = DAG( 'dag_scrape_from_foxsports',
                default_args=default_arguments,
                description='Extracting World Cup 22 Qatar data' ,
                schedule_interval = '@weekly',
                tags=['Web Scraping - Match Details'],
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
    def url_get_contents(url):
        # Opens a website and read its binary contents (HTTP Response Body)

        # Making request to the website
        req = urllib.request.Request(url=url)
        f = urllib.request.urlopen(req)

        # Reading contents of the website
        return f.read()

    # Defining the html contents of a URL.
    xhtml = url_get_contents('https://www.foxsports.com/soccer/fifa-world-cup-men/stats?category=goalkeeping&season=2022&groupId=12').decode('utf-8')
    xhtml1 = url_get_contents('https://www.foxsports.com/soccer/fifa-world-cup-men/team-stats?category=offensive&sort=t_sog&season=2022&sortOrder=desc&groupId=12').decode('utf-8')
    xhtml2 = url_get_contents('https://www.foxsports.com/soccer/fifa-world-cup-men/team-stats?category=defensive&season=2022&groupId=12').decode('utf-8')
    xhtml3 = url_get_contents('https://www.foxsports.com/soccer/fifa-world-cup-men/team-stats?category=defensive&season=2022&groupId=12').decode('utf-8')
    xhtml4 = url_get_contents('https://www.foxsports.com/soccer/fifa-world-cup-men/team-stats?category=standard&season=2022&groupId=12').decode('utf-8')
    xhtml5 = url_get_contents('https://www.foxsports.com/soccer/fifa-world-cup-men/stats?category=standard&season=2022&groupId=12').decode('utf-8')
    xhtml6 = url_get_contents('https://www.foxsports.com/soccer/fifa-world-cup-men/stats?category=control&season=2022&groupId=12').decode('utf-8')

    # Defining the HTMLTableParser object
    p = HTMLTableParser()
    p1 = HTMLTableParser()
    p2 = HTMLTableParser()
    p3 = HTMLTableParser()
    p4 = HTMLTableParser()
    p5 = HTMLTableParser()
    p6 = HTMLTableParser()

    # Feeding the html contents in the HTMLTableParser object
    p.feed(xhtml)
    p1.feed(xhtml1)
    p2.feed(xhtml2)
    p3.feed(xhtml3)
    p4.feed(xhtml4)
    p5.feed(xhtml5)
    p6.feed(xhtml6)

    # Dataframe
    pd1 = pd.DataFrame(p.tables[1])
    pd2 = pd.DataFrame(p1.tables[1])
    pd3 = pd.DataFrame(p2.tables[1])
    pd4 = pd.DataFrame(p3.tables[1])
    pd5 = pd.DataFrame(p4.tables[1])
    pd6 = pd.DataFrame(p5.tables[1])
    pd7 = pd.DataFrame(p6.tables[1])

        # Renaming columns
    pd1.set_axis(['No','Players','GP-Games Played',
                'GS-Games Started',	'MP-Minutes Played',
                'CS-Clean Sheets',	'GA-Goals Allowed',
                'SOG-Shots on Goal Against',	'SV-Saves',
                'SV%-Goalie Save Percentage',	'PKG-Penalty Kick Goals',
                'PK-Penalty Kicks',	'PKSV-Penalty Kick Saves',
                'YC-Yellow Cards',	'RC-Red Cards'
    ],
                axis='columns', inplace=True)

    pd2.set_axis(['No','Teams','GP-Games Played',
                'S-Shots',	'SOG-Shots On Goal',
                'SOP-Shots On Post',	'SOFF-Shots Off Target',
                'SAB-Shot Attempts Blocked',	'POSS-Possession Time Minutes Avg',
                'C-Crosses',	'CS-Crosses Successful',	'P-Passes',
                'PC-Pass Completions',	'PL-Pass Attempts - Long',
                'PLC-Pass Completions - Long',	'CK-Corner Kicks',
                'OFF-Offsides'
    ],
                axis='columns', inplace=True)

    pd3.set_axis(['No','Teams','GP-Games Played',	'TI-Throw Ins',
                'INT-Interceptions',	'TKL-Tackles',
                'TA-Tackles Attempted',	'GK-Goal Kicks',
                'F-Fouls',	'FK-Free Kicks',	'OG-Own Goals'
    ],
                axis='columns', inplace=True)

    pd4.set_axis(['No','Teams','GP-Games Played',	'GC-Goals Conceded',
                'S-Shots',	'SOG-Shots On Goal',	'SV-Saves',	'CLR-Clearances',
                'CS-Clean Sheets',	'PK-Penalty Kicks',	'PKG-Penalty Kick Goals'
    ],
                axis='columns', inplace=True)

    pd5.set_axis(['No','Teams','GP-Games Played',	'GF-Goals',
                'KG-Kicked Goals',	'HG-Header Goals',
                '1G-Goals First Half',	'2G-Goals Second Half',
                'GC-Goals Conceded',	'1GC-Goals Conceded First Half',
                '2GC-Goals Conceded Second Half',	'A-Assists',
                'PK-Penalty Kicks',	'PKG-Penalty Kick Goals',
                'YC-Yellow Cards',	'RC-Red Cards',	'YRC-Yellow Red Cards',
    ],
                axis='columns', inplace=True)

    pd6.set_axis(['No','Player','GP-Games Played',	'GS-Games Started',
                'MP-Minutes Played',	'G-Goals',	'HG-Header Goals',
                'PKG-Penalty Kick Goals',	'A-Assists',	'S-Shots',
                'SOG-Shots On Goal',	'SOFF-Shots Off Target',
                'OFF-Offsides','CK-Corner Kicks',	'YC-Yellow Cards',
                'RC-Red Cards',	'YRC-Yellow Red Cards'
    ],
                axis='columns', inplace=True)

    pd7.set_axis(['No','Player','GP-Games Played',	'GS-Games Started',
                'MP-Minutes Played',	'CC-Chances Created',
                'CS-Crosses Successful',	'C%-Cross Percentage',
                'PC-Pass Completions',	'P%-Pass Percentage',
                'PLC-Pass Completions - Long',	'PLC%-Pass Percentage - Long',
                'DBC-Dribbles Completed',	'LOP-Loss Of Possession'
    ],
                axis='columns', inplace=True)


    connection = engine.connect()
    # Saving dataframes in tables
    pd1.to_sql('clean_sheets', con=engine, index=False)
    pd2.to_sql('blocked_shots', con=engine, index=False)
    pd3.to_sql('tackles', con=engine, index=False)
    pd4.to_sql('penalty_kicks', con=engine, index=False)
    pd5.to_sql('cards', con=engine, index=False)
    pd6.to_sql('goals', con=engine, index=False)
    pd7.to_sql('pass', con=engine, index=False)
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

