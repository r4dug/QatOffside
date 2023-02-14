import requests
import pandas as pd
from bs4 import BeautifulSoup

# Request the website
url = "https://en.wikipedia.org/wiki/Herv%C3%A9_Renard"
response = requests.get(url)

# Use BeautifulSoup to parse the HTML
soup = BeautifulSoup(response.content, 'html.parser')

# Find the table in the HTML
table = soup.find('table', {'class': 'wikitable'})

# Use pandas to read the table and store it in a dataframe
df = pd.read_html(str(table))[0]
