from pathlib import Path
import pathlib
import argparse
import glob

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
        default="methods/*/results/*.csv")
    parser.add_argument("--output",
                        "-o",
                        help="file name of output. Default: users_merged.csv",
                        default="results/users_merged.csv")

    # Read arguments from the command line
    args = parser.parse_args()
    print(f"File arguments: {args.files}")

    data_files = []
    for file in args.files:
        if ("*" in file
            ):  # workaround for Windows shell not expanding asterisk
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
    df_github_names_long['github_user_id'] = df_github_names_long[
        'github_user_id'].str.lower()

    df_users = df_github_names_long[["github_user_id", "source"]].sort_values([
        "github_user_id", "source"
    ]).drop_duplicates(["github_user_id", "source"]).reset_index(drop=True)

    df_users['source'] = df_users['source'].map(lambda x: pathlib.PurePath(
        x).name)  # remove file path so the column only contains the file name

    df_users.to_csv(Path(args.output), index=False)
    print("Successfully merged users.")
