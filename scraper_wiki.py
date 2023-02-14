import pandas as pd
import requests
from bs4 import BeautifulSoup
import snowflake.connector
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

url = 'https://en.wikipedia.org/wiki/2022_FIFA_World_Cup'
wiki_dfs = pd.read_html(url)

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

##### Snowflake connection details

engine = create_engine(URL(
    account = 'cy81590.eu-central-1',
    user = 'R4DUG',
    password = 'WorldCup22',
    database = 'QAT_OFFSIDE',
    schema = 'PUBLIC',
    warehouse = 'COMPUTE_WH',
    role='ACCOUNTADMIN',
))

connection = engine.connect()
 
#df_bidders_cleaned.to_sql('bidders', con=engine, index=False) #make sure index is False, Snowflake doesnt accept indexes
#df_prizemoney_cleaned.to_sql('prize_money', con=engine, index=False)
#df_stadium_capacity.to_sql('stadiums', con=engine, index=False)
#df_teams_accomm.to_sql('team_accommodation', con=engine, index=False)
#df_group_A.to_sql('group_a_standings', con=engine, index=False)
#df_group_B.to_sql('group_b_standings', con=engine, index=False)
#df_group_C.to_sql('group_c_standings', con=engine, index=False)
#df_group_D.to_sql('group_d_standings', con=engine, index=False)
#df_group_E.to_sql('group_e_standings', con=engine, index=False)
#df_group_F.to_sql('group_f_standings', con=engine, index=False)
#df_group_G.to_sql('group_g_standings', con=engine, index=False)
#df_group_H.to_sql('group_h_standings', con=engine, index=False)
#df_transformed_awards.to_sql('awards', con=engine, index=False)


 
connection.close()
engine.dispose()



print(wiki_dfs[92])
