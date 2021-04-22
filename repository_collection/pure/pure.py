from pathlib import Path

import rispy
import pandas as pd

def get_username_from_text(text):
    for word in text:
        if "github.com" in word:
            split = word.split("github.com/")
            # get value after "github.com/" and split after the next slash, then the first value of that split will be the username
            user = split[1].split("/")[0]
            return user
        elif "github.io" in word:
            githubio_split = word.split(".")
            user = githubio_split[0].split("://")[1]
            return user
    return None

filepath = r"repository_collection\pure\Pure_160421.ris" 
users = list()
with open(filepath, 'r', encoding="utf8") as pure_data:
    entries = rispy.load(pure_data)
    for entry in entries:
        user = get_username_from_text(entry.values())
        if (user is not None):
            users.append(user)
            
    pd.Series(users, name = "github_user_id").to_csv(Path("repository_collection", "pure", "results", "ids_pure_users.csv"), index = False)
    


