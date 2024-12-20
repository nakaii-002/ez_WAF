import pandas as pd
import re

data = pd.read_csv('csic_database.csv')
# data['path'] = data.apply(lambda x : x['URL'].replace('http://' + x['host'], '', 1), axis=1)
data['path'] = data.apply(lambda x : re.findall(r"^[^:]+://[^/]+(/[^?#\s]*\??[^#\s]*)?", x['URL'])[0], axis=1)
data.drop(columns=['connection', 'lenght', 'URL', 'Type', data.columns[0], 'Pragma', 'Cache-Control', 'Accept', 'Accept-encoding', 'Accept-charset', 'language', 'host'],inplace=True)
data.to_csv('csic_database_cleaned.csv',index=False)