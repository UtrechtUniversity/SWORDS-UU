"""
This file automatically filters out duplicates, github.io repositories and forks.
"""
from datetime import datetime
import argparse

import pandas as pd

# Initiate the parser
parser = argparse.ArgumentParser()

# Add arguments to be parsed
parser.add_argument("--input",
                    "-i",
                    help="The file name of the retrieved repositories.",
                    default="results/repositories.csv")
parser.add_argument("--output",
                    "-o",
                    help="The file name of the filtered repositories.",
                    default="results/repositories_filtered.csv")


def read_input_file(file_path):
    """reads in the input file through Pandas

    Args:
        file_path (string): path to the file

    Returns:
        DataFrame
    """
    if "xlsx" in file_path:
        file = pd.read_excel(file_path, engine='openpyxl')
    else:
        file = pd.read_csv(file_path)
    return file


# Read arguments from the command line
args = parser.parse_args()
print(f"Filtering repositories for the following file: {args.input}")
df_repos = read_input_file(args.input)

num_total = len(df_repos.index)

#drop duplicates
df_repos.drop_duplicates(subset='id', inplace=True)
print(f"Filtered {num_total - len(df_repos.index)} of {num_total}"
      " total repositories by dropping duplicates.")
#drop forks
df_repos = df_repos[~df_repos.fork]
print(f"Filtered {num_total - len(df_repos.index)} of {num_total}"
      " total repositories by dropping forks.")
df_repos.reset_index(drop=True, inplace=True)

# drop github.io repos
df_repos_filtered = df_repos[~df_repos.name.str.contains("github.io")]
print(
    f"Filtered {len(df_repos.index) - len(df_repos_filtered.index)} of {num_total}"
    " total repositories by dropping github.io repositories.")

num_final = len(df_repos_filtered.index)
num_filtered = num_total - num_final

print(f"Filtered {num_filtered} of {num_total} repositories. {num_final}"
      " repositories left.")

current_date = datetime.today().strftime('%Y-%m-%d')
df_repos_filtered = df_repos_filtered.assign(date=current_date)

if "xlsx" in args.output:
    df_repos_filtered.to_excel(args.output, index=False)
else:
    df_repos_filtered.to_csv(args.output, index=False)

print(
    f"Successfully filtered user repositories. Saved result to {args.output}.")
