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
                    help="file name of input. Default: users_merged.csv",
                    required=True)
parser.add_argument(
    "--update",
    "-u",
    action='store_true',
    help=
    "Update everything including existing users or only add new ones. Default is False",
    default=False)
parser.add_argument(
    "--fileupdate",
    "-fu",
    help=
    "If you want to update an existing file, provide a file name in this argument. Example: 'unique_users_annotated.xlsx'"
)
parser.add_argument("--output",
                    "-o",
                    help="file name of output. Default: users_enriched.csv",
                    default="results/users_enriched.csv")

# Read arguments from the command line
args = parser.parse_args()


def read_pandas_file(file_path):
    if ("xlsx" in file_path):
        return pd.read_excel(file_path, engine='openpyxl')
    else:
        return pd.read_csv(file_path)


df_users = read_pandas_file(args.input)
df_users = df_users.drop_duplicates("github_user_id").reset_index(drop=True)

UPDATE_EVERYTHING = args.update

if (args.fileupdate):
    try:
        # If this block is successfully executed it is an update of users
        df_users_annotated = read_pandas_file(args.fileupdate)
        df_users["new_user"] = False
        df_users.loc[~df_users["github_user_id"].
                     isin(df_users_annotated["github_user_id"].str.lower()),
                     "new_user"] = True
    except FileNotFoundError:
        print("No file with annotated user data yet available.")
    try:
        print("New users:")
        print(df_users[df_users["new_user"] == True])
    except KeyError:
        print("No new users.")


def get_userdata(user_list, api, sleep=6):
    results_github_user_api = []
    for index, user_id in enumerate(user_list):
        try:
            user = dict(api.users.get_by_username(user_id))
            if (
                    len(user) > 32
            ):  # if the authenticated user is retrieved, there will be extra variables
                entries_to_remove = ('private_gists', 'total_private_repos',
                                     'owned_private_repos', 'disk_usage',
                                     'collaborators',
                                     'two_factor_authentication', 'plan')
                for k in entries_to_remove:
                    user.pop(k, None)
            results_github_user_api.append(user)
        except Exception as e:
            print("User %s encountered an error." % user_id)
            print(e)
        if (index % 10 == 0):
            print("Processed %d out of %d users." % (index, len(user_list)))
        time.sleep(sleep)
    return pd.DataFrame(results_github_user_api)


def update_users(df_users_annotated, df_new_users):
    df_users = df_users_annotated.copy()  # don't modify initial df
    for row_new in df_new_users.iterrows():  # iterate over rows in first df
        # get github_user_id from this row
        github_user_id = row_new[1]['login']
        # get keys and values
        keys, values = zip(*[(key, value) for key, value in row_new[1].items()
                             if key != "login"])
        #         print(keys)
        # find row index in df2 where login value corresponds to github_user_id, if it exists
        index_row_annotated = df_users.index[df_users['github_user_id'] ==
                                             github_user_id]
        if (len(index_row_annotated) > 0):  # user exists already
            df_users.loc[index_row_annotated, keys] = values
            pass
        else:  # user doesn't exist yet - insert
            new_index = df_users.index[-1] + 1
            df_users.loc[new_index, "github_user_id"] = github_user_id
            df_users.loc[new_index, keys] = values
    return df_users


# Automatic filtering of students
def is_student(user_bio):
    """Checks whether a GitHub user is a student. The bio of a user is parsed. 
    If it contains phd the user will not be marked as a student. 
    If the bio contains only the word student the user will be marked as a student. If

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


load_dotenv()
# if unauthorized API is used, rate limit is lower leading to a ban and waiting time needs to be increased
token = os.getenv('GITHUB_TOKEN')
api = GhApi(token=token)

if (token is not None):  # authentication
    sleep = 2
else:  # no authentication
    sleep = 6

if 'new_user' in df_users.columns:  # updating users
    if (UPDATE_EVERYTHING == True):
        df_users_all = pd.merge(df_users[df_users["new_user"] == True].drop(
            ["source"], axis=1),
                                df_users_annotated,
                                on="github_user_id",
                                how="outer")
        results_github_user_api = get_userdata(df_users_all["github_user_id"],
                                               api, sleep)

    else:  # only add new users
        df_users_update = pd.merge(df_users[df_users["new_user"] == True],
                                   df_users_annotated,
                                   left_on="github_user_id",
                                   right_on="github_user_id",
                                   how="left")
        results_github_user_api = get_userdata(
            df_users_update["github_user_id"], api, sleep)

    df_users_enriched = update_users(df_users_annotated,
                                     results_github_user_api)
    df_users_enriched["is_student"] = df_users_enriched['bio'].apply(
        is_student)

else:  # first time collecting data
    results_github_user_api = get_userdata(df_users["github_user_id"], api,
                                           sleep)
    df_users_enriched = df_users.merge(results_github_user_api,
                                       left_on="github_user_id",
                                       right_on="login",
                                       how="left")
    df_users_enriched.drop(["login"], axis=1, inplace=True)
    df_users_enriched = df_users_enriched.reindex(
        columns=df_users_enriched.columns.tolist() + [
            "is_student", "is_employee", "is_currently_employed",
            "is_research_group", "final_decision", "note"
        ])
    df_users_enriched["is_student"] = df_users_enriched['bio'].apply(
        is_student)

print(
    f"How many users are students? \n {df_users_enriched['is_student'].value_counts().to_frame()}"
)

if ("xlsx" in args.output):
    df_users_enriched.to_excel(args.output, index=False)
else:
    df_users_enriched.to_csv(args.output, index=False)

print("Successfully enriched users.")
