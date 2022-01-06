"""
Enrich merged users from the merge_users.py output. Enriching means fetching the Github API data.
"""
import argparse
import os
import time
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
from ghapi.all import GhApi


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


def get_userdata(user_list):
    """Retrieves Github userdata from a list of users

    Args:
        user_list (list): list of Github usernames

    Returns:
        DataFrame: Complete dataframe with enriched users
    """
    github_data = []
    for index, user_id in enumerate(user_list):
        try:
            user = dict(api.users.get_by_username(user_id))
            if len(
                    user
            ) > 32:  # if the authenticated user is retrieved, there will be extra variables
                entries_to_remove = ('private_gists', 'total_private_repos',
                                     'owned_private_repos', 'disk_usage',
                                     'collaborators',
                                     'two_factor_authentication', 'plan')
                for k in entries_to_remove:
                    user.pop(k, None)
            github_data.append(user)
        except Exception as e: # pylint: disable=broad-except
            print(f"User {user_id} encountered an error.")
            print(e)
        if index % 10 == 0:
            print(f"Processed {index} out of {len(user_list)} users.")
        time.sleep(SLEEP)
    return pd.DataFrame(github_data)


def update_users(df_users_passed, df_new_users):
    """Updates already enriched users with new data

    Args:
        df_users_passed (DataFrame): Enriched users
        df_new_users (DataFrame): New users

    Returns:
        DataFrame: Merged Dataframe with updated users
    """
    df_users_copy = df_users_passed.copy()  # don't modify initial df
    for row_new in df_new_users.iterrows():  # iterate over rows in first df
        # get user_id from this row
        user_id = row_new[1]['login']
        # get keys and values
        keys, values = zip(*[(key, value) for key, value in row_new[1].items()
                             if key != "login"])
        # find row index in df2 where login value corresponds to user_id, if it exists
        index_row_annotated = df_users_copy.index[df_users_copy['user_id'] ==
                                                  user_id]
        if len(index_row_annotated) > 0:  # user exists already
            df_users_copy.loc[index_row_annotated, keys] = values
        else:  # user doesn't exist yet - insert
            new_index = df_users_copy.index[-1] + 1
            df_users_copy.loc[new_index, "user_id"] = user_id
            df_users_copy.loc[new_index, keys] = values
    return df_users_copy


if __name__ == '__main__':

    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument("--input",
                        "-i",
                        help="file name of input.",
                        default="results/users_merged.csv")
    parser.add_argument(
        "--update",
        "-u",
        action='store_true',
        help=
        "Update everything including existing users or only add new ones. Default is False"
    )
    parser.add_argument(
        "--fileupdate",
        "-fu",
        help=
        "If you want to update an existing file, provide a file name in this argument."
    )
    parser.add_argument("--output",
                        "-o",
                        help="file name of output.",
                        default="results/users_enriched.csv")

    # Read arguments from the command line
    args = parser.parse_args()

    df_users = read_input_file(args.input)
    df_users = df_users.drop_duplicates("user_id").reset_index(drop=True)

    UPDATE_EVERYTHING = args.update

    if args.fileupdate:
        try:
            # If this block is successfully executed it is an update of users
            df_users_annotated = read_input_file(args.fileupdate)
            df_users["new_user"] = False
            df_users.loc[~df_users["user_id"].
                         isin(df_users_annotated["user_id"].str.lower()),
                         "new_user"] = True
        except FileNotFoundError:
            print("No file with annotated user data yet available.")
        try:
            print("New users:")
            print(df_users[df_users["new_user"] is True])
        except KeyError:
            print("No new users.")

    load_dotenv()
    # if unauthorized API is used, rate limit is lower leading to a ban and
    # waiting time needs to be increased
    token = os.getenv('GITHUB_TOKEN')
    api = GhApi(token=token)

    if token is not None:  # authentication
        SLEEP = 2
    else:  # no authentication
        SLEEP = 6

    if 'new_user' in df_users.columns:  # updating users
        if UPDATE_EVERYTHING is True:
            df_users_all = pd.merge(
                df_users[df_users["new_user"] is True].drop(["source"],
                                                            axis=1),
                df_users_annotated,
                on="user_id",
                how="outer")
            results_github_user_api = get_userdata(df_users_all["user_id"])

        else:  # only add new users
            df_users_update = pd.merge(df_users[df_users["new_user"] is True],
                                       df_users_annotated,
                                       left_on="user_id",
                                       right_on="user_id",
                                       how="left")
            results_github_user_api = get_userdata(df_users_update["user_id"])

        df_users_enriched = update_users(df_users_annotated,
                                         results_github_user_api)
    else:  # first time collecting data
        results_github_user_api = get_userdata(df_users["user_id"])
        results_github_user_api["login"] = results_github_user_api[
            "login"].str.lower(
            )  # key to merge is lowercase so this needs to be lowercase as well
        df_users_enriched = df_users.merge(results_github_user_api,
                                           left_on="user_id",
                                           right_on="login",
                                           how="left")
        df_users_enriched.drop(["login"], axis=1, inplace=True)

    current_date = datetime.today().strftime('%Y-%m-%d')
    df_users_enriched["date"] = current_date
    if "xlsx" in args.output:
        df_users_enriched.to_excel(args.output, index=False)
    else:
        df_users_enriched.to_csv(args.output, index=False)

    print("Successfully enriched users.")
