"""
Prepare enriched data to be manually filtered.
This file adds columns and info whether a user is a student.
"""
import argparse
from datetime import datetime

import pandas as pd


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


def is_student(user_bio):
    """Checks whether a GitHub user is a student.

    The bio of a user is parsed. If it contains phd the user will not be
    marked as a student. If the bio contains only the word student the user
    will be marked as a student.

    Args:
        user_id (string): user id which is named as "login" from the GitHub Api

    Returns:
        Boolean: Whether the user is a student or not
    """
    user_bio = str(user_bio).lower()
    student = False
    if user_bio != "nan":
        # PhD students should be included
        mention_phd = "phd" in user_bio
        mention_student = "student" in user_bio
        student = not mention_phd and mention_student
    return student


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--input",
                        "-i",
                        help="file name of input.",
                        default="results/users_enriched.csv")
    parser.add_argument("--output",
                        "-o",
                        help="file name of output.",
                        default="results/users_enriched.csv")
    args = parser.parse_args()

    df_users_enriched = read_input_file(args.input)

    df_users_enriched["is_student"] = df_users_enriched['bio'].apply(
        is_student)

    print("Successfully added is_student column.")
    print("How many users are students? \n "
          f"{df_users_enriched['is_student'].value_counts().to_frame()}")

    columns_to_add = [
        "is_employee", "is_currently_employed", "is_research_group",
        "final_decision", "note"
    ]

    print("Adding empty columns to dataframe...")
    for column in columns_to_add:
        if column not in df_users_enriched:
            df_users_enriched = pd.concat(
                [df_users_enriched,
                 pd.DataFrame(columns=[column])])
        else:
            print(
                f"Column {column} already exists. This column will be skipped."
            )
    print("Successfully added columns.")

    current_date = datetime.today().strftime('%Y-%m-%d')
    df_users_enriched["date"] = current_date
    if "xlsx" in args.output:
        df_users_enriched.to_excel(args.output, index=False)
    else:
        df_users_enriched.to_csv(args.output, index=False)

    print("Successfully prepared filtering.")
