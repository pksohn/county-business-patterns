import pandas as pd
import requests
import secrets

# DOWNLOAD MASTER NAICS CODE LIST FOR 2014

baseurl = 'http://api.census.gov/data/2014/cbp'
cbp_vars = 'NAICS2012,NAICS2012_TTL,GEO_TTL'
key = secrets.censuskey

url = '{baseurl}?get={cbp_vars}&for=us:*&key={key}'.format(**locals())
req = requests.get(url)

naics = pd.read_json(req.text)
naics.columns = naics.loc[0]
naics = naics.loc[1:]
naics = naics.loc[:, ['NAICS2012', 'NAICS2012_TTL']]

naics.to_csv('naics_list.csv', index=False)
