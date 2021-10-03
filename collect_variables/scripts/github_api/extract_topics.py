# split topics into their own dataset
from pathlib import Path
from datetime import datetime
import ast

import pandas as pd

df_repos = pd.read_csv(
    Path("variable_collection", "output",
         "repositories_filtered_2021-05-20.csv"))
variables = []
for (url, topics_str) in zip(df_repos["html_url"], df_repos["topics"]):
    topics = ast.literal_eval(topics_str)
    if (len(topics) > 0):
        for topic in topics:
            entry = [url, topic]
            variables.append(entry)

print(variables)

df_data = pd.DataFrame(variables, columns=["html_url_repository", "topic"])
current_date = datetime.today().strftime('%Y-%m-%d')
df_data.to_csv(Path("variable_collection", "output",
                    "topics_" + current_date + ".csv"),
               index=False)
