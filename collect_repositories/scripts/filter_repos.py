import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

df_repos = pd.read_csv(Path("repository_collection", "repositories.csv"))

# drop github.io repos
df_repos = df_repos[~df_repos.name.str.contains("github.io")]
# df_repos['size'].replace('', np.nan, inplace=True)
# df_repos.dropna(subset=['size'], inplace=True)
# df_repos[df_repos.size != 0]

#drop duplicates
df_repos.drop_duplicates(subset='id', inplace=True)
df_repos.reset_index(drop=True, inplace=True)

current_date = datetime.today().strftime('%Y-%m-%d')
df_repos.to_csv(Path("variable_collection", "output",
                     "repositories_filtered" + "_" + current_date + ".csv"),
                index=False)
