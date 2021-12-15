"""
This file retrieves repositories from a file of users.
"""
import os
import time
import argparse
from datetime import datetime

from ghapi.all import GhApi, pages
from fastcore.foundation import L, AttrDict
import pandas as pd
from dotenv import load_dotenv


def get_repos(user_id):
    """retrieves complete repositories (exluding forked ones) from a specified user_id

    Args:
        api (GhApi object): standard Api object from GhApi
        user_id (string): user id which is named as "login" from the GitHub Api

    Returns:
        L: fastcore list of repositories
    """
    try:
        # do first request to store last page variable in api object.
        # If more than one page is available, another request needs to be made.
        print(f"Fetching repos for user '{user_id}'")
        query_result = api.repos.list_for_user(user_id, per_page=100)
    except Exception as e: # pylint: disable=broad-except
        print(
            f"There was a problem with fetching repositories for user {user_id}"
        )
        print(e)
        return None
    result = L()
    num_pages = api.last_page()
    if num_pages > 0:
        query_result = pages(api.repos.list_for_user, num_pages, user_id)
        for page in query_result[0]:
            result.append(page)
        time.sleep(2)
    else:
        result.extend(query_result)
    return result


def get_repos_formatted(repos_unformatted):
    """Goes through a list of repos and returns them correctly formatted

    Args:
        repos (L): fastcore foundation list of repositories

    Returns:
        L: fastcore founation list of complete repository data
    """
    result = L()
    for repo in repos_unformatted:
        repo_dict = dict(repo)
        result.append(repo_dict)
    return result


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


if __name__ == '__main__':

    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument("--users",
                        "-u",
                        help="The path to the file with enriched users.",
                        default="../collect_users/results/users_enriched.xlsx")
    parser.add_argument(
        "--output",
        "-o",
        help="The file name of the repositories that are retrieved.",
        default="results/repositories.csv")

    # Read arguments from the command line
    args = parser.parse_args()
    print(f"Retrieving repositories for the following file: {args.users}")

    load_dotenv()
    # if unauthorized API is used, rate limit is lower,
    # leading to a ban and waiting time needs to be increased
    token = os.getenv('GITHUB_TOKEN')
    api = GhApi(token=token)
    df_users = read_input_file(args.users)

    # drop filtered users
    df_users = df_users.drop(df_users[df_users.final_decision == 0].index)

    result_repos = []
    COUNTER = 0
    for user in df_users["user_id"]:
        repos = get_repos(user)
        if repos is not None:
            repos_formatted = get_repos_formatted(repos)
            result_repos.extend(repos_formatted)
        else:
            print(f"User {user} has no repositories.")
        time.sleep(2.1)
        if COUNTER % 10 == 0:
            print(f"Processed {COUNTER} out of {len(df_users.index)} users.")
        COUNTER += 1

    print("Finished processing users. Flattening nested structures...")
    # Flatten nested structures
    for i, _ in enumerate(result_repos):
        for key in result_repos[i].keys():
            if isinstance(result_repos[i][key], AttrDict):
                if key == "owner":
                    result_repos[i][key] = result_repos[i][key]["login"]
                elif key == "permissions":
                    result_repos[i][key] = ""
                elif key == "license":
                    result_repos[i][key] = result_repos[i][key]["name"]

    df_result_repos = pd.DataFrame(result_repos)
    current_date = datetime.today().strftime('%Y-%m-%d')
    df_result_repos["date"] = current_date
    df_result_repos.to_csv(args.output, index=False)

    print(
        f"Successfully retrieved user repositories. Saved result to {args.output}."
    )
