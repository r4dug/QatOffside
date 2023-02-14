import requests
import pandas as pd
from bs4 import BeautifulSoup
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

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
    df = pd.read_html(str(table))[0]
    dataframes.append(df)

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
df.to_sql('manager_age', con=engine, index=False)
connection.close()
engine.dispose()