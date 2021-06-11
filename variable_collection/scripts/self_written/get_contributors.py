import os
import time
from pathlib import Path
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
import requests


# if unauthorized API is used, rate limit is lower leading to a ban and waiting time needs to be increased
load_dotenv()
token = os.getenv('GITHUB_TOKEN')
headers = {'Authorization': 'token ' + token}
params = {
    'per_page': 100,
}

df_repos = pd.read_csv(Path("variable_collection", "output", "repositories_filtered_2021-05-20.csv"))
if(token is None):
    sleep = 6
else:
    sleep = 2


# get column names
url = "https://api.github.com/repos/beld78/HTML-Examples/contributors" # arbitrary repo to retrieve column names
r = requests.get(url=url, headers=headers)
data = r.json()
if isinstance(data, list):
    column_headers = list(data[0].keys())
    print(column_headers)
    all_column_headers = ["html_url_repository"] + column_headers
    print(all_column_headers)
    time.sleep(sleep)
else:
    print("There was an error retrieving column names.")

# get data
variables = []
for counter, (url, contributor_url) in enumerate(zip(df_repos["html_url"].head(5), df_repos["contributors_url"].head(5))):
    request_successful = False
    while(not request_successful):
        r = requests.get(url=contributor_url, headers=headers, params=params)
        print(r, contributor_url)
        if (r.status_code == 200): 
            data = r.json()
            for contributor in data:
                entry = [url]
                entry.extend(list(contributor.values()))
                print(entry[0:2])
                variables.append(entry)
        elif(r.status_code == 403): # timeout
            print("There was a problem: %s" % contributor_url)
            print("Sleep for a while.")
            for i in range(100):
                time.sleep(6)
                continue
        elif(r.status_code in [204, 404]): # (non-existing repo)
            print("Repository does not exist: %s" % url)
        else:
            print("Unhandled status code: %d - skip repository" % r.status_code)
            
        request_successful = True
        time.sleep(sleep)
        
        if(counter % 10 == 0):
            print("Parsed %d repos." % counter)
            
df_data = pd.DataFrame(variables, columns=all_column_headers)
current_date = datetime.today().strftime('%Y-%m-%d')
df_data.to_csv(Path("variable_collection", "output", "contributors_"+current_date+".csv"), index=False)