from pathlib import Path
import argparse
import os
import time
from dotenv import load_dotenv

from ghapi.all import GhApi
import pandas as pd

# Initiate the parser
parser = argparse.ArgumentParser()

# Add arguments to be parsed
parser.add_argument("--input",
                    "-i",
                    help="file name of input.",
                    default="results/users_enriched.csv")
parser.add_argument("--output",
                    "-o",
                    help="file name of output.",
                    default="results/users_enriched.csv")


def read_pandas_file(file_path):
    if ("xlsx" in file_path):
        return pd.read_excel(file_path, engine='openpyxl')
    else:
        return pd.read_csv(file_path)


# Flagging of students
def is_student(user_bio):
    """Checks whether a GitHub user is a student. The bio of a user is parsed. 
    If it contains phd the user will not be marked as a student. 
    If the bio contains only the word student the user will be marked as a student.

    Args:
        user_id (string): user id which is named as "login" from the GitHub Api 

    Returns:
        Boolean: Whether the user is a student or not
    """
    user_bio = str(user_bio).lower()
    if (user_bio != "nan"):
        # PhD students should be included
        mention_phd = "phd" in user_bio
        mention_student = "student" in user_bio
        return (not mention_phd and mention_student)
    else:
        # we can't be sure and therefore keep the user
        return False


# Read arguments from the command line
args = parser.parse_args()

df_users_enriched = read_pandas_file(args.input)

df_users_enriched["is_student"] = df_users_enriched['bio'].apply(is_student)

print("Successfully added is_student column.")
print(
    f"How many users are students? \n {df_users_enriched['is_student'].value_counts().to_frame()}"
)

columns_to_add = [
    "is_employee", "is_currently_employed", "is_research_group",
    "final_decision", "note"
]

print("Adding empty columns to dataframe...")
for column in columns_to_add:
    if (column not in df_users_enriched):
        df_users_enriched = pd.concat(
            [df_users_enriched,
             pd.DataFrame(columns=[column])])
    else:
        print(f"Column {column} already exists. This column will be skipped.")
print("Successfully added columns.")

if ("xlsx" in args.output):
    df_users_enriched.to_excel(args.output, index=False)
else:
    df_users_enriched.to_csv(args.output, index=False)

print("Successfully prepared filtering.")
