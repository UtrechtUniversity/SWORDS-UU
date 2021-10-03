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

df_repos = pd.read_csv(
    Path("variable_collection", "output",
         "repositories_filtered_2021-05-20.csv"))
if (token is None):
    sleep = 6
else:
    sleep = 2

# get languages
variables = []
for counter, (url, languages_url) in enumerate(
        zip(df_repos["html_url"], df_repos["languages_url"])):
    request_successful = False
    while (not request_successful):
        r = requests.get(url=languages_url, headers=headers)
        print(r, url, languages_url)
        if (r.status_code == 200):
            data = r.json()
            print(data.items())
            for language, num_chars in data.items():
                entry = [url]
                entry.extend([language, num_chars])
                print(entry)
                variables.append(entry)
        elif (r.status_code == 403):  # timeout
            print("There was a problem: %s" % languages_url)
            print("Sleep for a while.")
            for i in range(100):
                time.sleep(6)
                continue
        elif (r.status_code in [204, 404]):  # (non-existing repo)
            print("Repository does not exist: %s" % url)
        else:
            print("Unhandled status code: %d - skip repository" %
                  r.status_code)

        request_successful = True
        time.sleep(sleep)
        if (counter % 10 == 0):
            print("Parsed %d repos." % counter)

df_data = pd.DataFrame(
    variables, columns=["html_url_repository", "language", "num_chars"])
current_date = datetime.today().strftime('%Y-%m-%d')
df_data.to_csv(Path("variable_collection", "output",
                    "languages_" + current_date + ".csv"),
               index=False)
