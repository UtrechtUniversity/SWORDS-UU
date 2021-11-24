from pathlib import Path
from datetime import datetime
import argparse

import pandas as pd

# Initiate the parser
parser = argparse.ArgumentParser()

# Add arguments to be parsed
parser.add_argument("--input",
                    "-i",
                    help="The file name of the retrieved repositories.",
                    required=True)
parser.add_argument(
    "--output",
    "-o",
    help=
    "The file name of the filtered repositories. Note that there will always be a timestamp added to the file name in the following format: YYYY-MM-DD. Default value: repositories_filtered",
    default="results/repositories_filtered")


def read_pandas_file(file_path):
    if ("xlsx" in file_path):
        return pd.read_excel(file_path, engine='openpyxl')
    else:
        return pd.read_csv(file_path)


# Read arguments from the command line
args = parser.parse_args()
print(f"Filtering repositories for the following file: {args.input}")
df_repos = read_pandas_file(args.input)

num_total = len(df_repos.index)

#drop duplicates
df_repos.drop_duplicates(subset='id', inplace=True)
print(
    f"Filtered {num_total - len(df_repos.index)} of {num_total} total repositories by dropping duplicates."
)
#drop forks
df_repos = df_repos[df_repos['fork'] == False]
print(
    f"Filtered {num_total - len(df_repos.index)} of {num_total} total repositories by dropping forks."
)
df_repos.reset_index(drop=True, inplace=True)

# drop github.io repos
df_repos_filtered = df_repos[~df_repos.name.str.contains("github.io")]
print(
    f"Filtered {len(df_repos.index) - len(df_repos_filtered.index)} of {num_total} total repositories by dropping github.io repositories."
)

num_final = len(df_repos_filtered.index)
num_filtered = num_total - num_final

print(
    f"Filtered {num_filtered} of {num_total} repositories. {num_final} repositories left."
)

current_date = datetime.today().strftime('%Y-%m-%d')
output_path = args.output + "_" + current_date + ".csv"
df_repos_filtered.to_csv(Path(output_path), index=False)

print(
    f"Successfully filtered user repositories. Saved result to {output_path}.")
