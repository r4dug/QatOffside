import pandas as pd
import requests
from bs4 import BeautifulSoup
import snowflake.connector
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

### urls ###
market_value_url = 'https://bolavip.com/en/qatar2022/qatar-2022-list-of-50-world-cup-players-with-the-highest-market-value-20221117-0021.html'
no_world_cup_apps_url = 'https://en.wikipedia.org/wiki/National_team_appearances_in_the_FIFA_World_Cup'
manager_appnmtyear_url = 'https://worldsoccertalk.com/news/foreign-born-managers-seek-rare-successes-at-world-cup-2022-20220802-CMS-394875.html'
manager_origin_url = 'https://footballnewzz.com/world-cup-coaches-2022-qatar/'
saudi_arabia_manager_url = 'https://en.wikipedia.org/wiki/Herv%C3%A9_Renard'

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

### manager appointment year ###
manager_origin_list = pd.read_html(manager_origin_url)
df_manager_origin = manager_origin_list[0]

### managerial career ###
wiki = pd.read_html(saudi_arabia_manager_url)
df_rwar = wiki[1]
print(df_rwar)

engine = create_engine(URL(
    account='jnsqfyg-yu12859',
    user='adinai',
    password='WorldCup22',
    database='QAT_OFFSIDE',
    schema='public',
    warehouse = 'COMPUTE_WH',
    role='ACCOUNTADMIN'
))

connection = engine.connect()
#df_market_value.to_sql('player_market_value', con=engine, index=False)
#df_worldcup_apps.to_sql('world_cup_team_apps', con=engine, index=False)
#df_manager_appnmtyear.to_sql('manager_appnmt_year', con=engine, index=False)
#df_manager_origin.to_sql('manager_origin', con=engine, index=False)
connection.close()
engine.dispose()
