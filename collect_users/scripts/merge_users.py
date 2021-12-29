"""
Merges users from the different retrieval methods
"""
import argparse
import glob
import pathlib
from pathlib import Path
from datetime import datetime

import pandas as pd

if __name__ == '__main__':

    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument(
        "--files",
        "-f",
        nargs="*",
        help="set file paths to be merged. Example: methods/*/results/*.csv",
        default=["methods/*/results/*.csv"])
    parser.add_argument("--output",
                        "-o",
                        help="file name of output. Default: users_merged.csv",
                        default="results/users_merged.csv")

    # Read arguments from the command line
    args = parser.parse_args()
    print(f"File arguments: {args.files}")

    data_files = []
    for file in args.files:
        if "*" in file:  # workaround for Windows shell not expanding asterisk
            data_files.extend(glob.glob(file))
        else:
            data_files.append(file)

    print(f"Parsing files for... \n {data_files}")
    df_github_names_long = pd.concat(
        [pd.read_csv(fp) for fp in data_files],
        axis=0,
        keys=data_files,
        names=["source", "row"]).reset_index("source").reset_index(drop=True)
    # lowercase to remove duplicates correctly
    df_github_names_long['user_id'] = df_github_names_long[
        'user_id'].str.lower()

    df_users = df_github_names_long[[
        "user_id", "source", "service"
    ]].sort_values(["user_id", "source",
                    "service"]).drop_duplicates(["user_id", "source"
                                                 ]).reset_index(drop=True)

    df_users['source'] = df_users['source'].map(lambda x: pathlib.PurePath(
        x).name)  # remove file path so the column only contains the file name

    current_date = datetime.today().strftime('%Y-%m-%d')
    df_users["date"] = current_date
    df_users.to_csv(Path(args.output), index=False)
    print("Successfully merged users.")
