import os
import time
from pathlib import Path
from datetime import datetime
import json 

import pandas as pd
from dotenv import load_dotenv
import requests


# if unauthorized API is used, rate limit is lower leading to a ban and waiting time needs to be increased
load_dotenv()
token = os.getenv('GITHUB_TOKEN')
headers = {'Authorization': 'token ' + token}

languages = pd.read_csv(Path("variable_collection", "output", "languages_2021-05-22.csv"))

if(token is None):
    sleep = 6
else:
    sleep = 2
    
    
variables = []
counter = 0
languages_jupyter = languages[languages["language"] == "Jupyter Notebook"].drop(["language", "num_chars"], axis=1)
print("Parse %d repos." % len(languages_jupyter["html_url_repository"]))
for repo_url in languages_jupyter["html_url_repository"]:
    repo_string = repo_url.split("github.com/")[1]    
    api_string = "https://api.github.com/repos/"+repo_string+"/git/trees/master?recursive=1" # see: https://stackoverflow.com/a/61656698/5708610
    request_successful = False
    while(not request_successful):
        r = requests.get(url=api_string, headers=headers)
        print(r, repo_url)
        if (r.status_code == 200): 
            data = r.json()
            for file in data["tree"]:
                if(file["type"] == "blob" and ".ipynb" in file["path"]):
                    entry = [repo_url, file["path"]]
                    print(entry)
                    variables.append(entry)
        elif(r.status_code == 403): # timeout
            print("There was a problem: %s" % contributor_url)
            print("Sleep for a while.")
            for i in range(100):
                time.sleep(6)
                continue
        elif(r.status_code in [204, 404]): # (non-existing repo)
            print("Repository does not exist: %s" % repo_url)
        else:
            print("Unhandled status code: %d - skip repository" % r.status_code)
            
        request_successful = True
        counter += 1
        time.sleep(sleep)
        if(counter % 10 == 0):
            print("Parsed %d repos." % counter)
            