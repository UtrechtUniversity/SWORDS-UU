import os
import time
from pathlib import Path

from ghapi.all import GhApi, pages
from fastcore.foundation import L
import pandas as pd
from dotenv import load_dotenv


def get_repos(api, user_id):
    """retrieves complete repositories (exluding forked ones) from a specified user_id

    Args:
        api (GhApi object): standard Api object from GhApi
        user_id (string): user id which is named as "login" from the GitHub Api

    Returns:
        L: fastcore list of repositories
    """
    try:
        # do first request to store last page variable in api object. If more than one page is available, another request needs to be made
        query_result = api.search.repos("user:" + user_id, per_page = 100)
    except Exception as e:
        print("There was a problem with fetching repositories for user %s" % user_id)
        print(e)
        return (None, 1)
    requests = 1
    result = L()
    if(api.last_page() > 0):
        query_result = pages(api.search.repos, api.last_page(), "user:" + user_id)
        requests += 1
        for page in query_result:
            result.extend(page["items"])
    else:
        result.extend(query_result["items"])
    return (result, requests)

def get_full_name_from_repos(repos):
    """Goes through a list of repos and returns their url

    Args:
        repos (L): fastcore foundation list of repositories

    Returns:
        L: fastcore founation list of full names
    """
    result = L()
    for repo in repos:
        result.append(repo["full_name"])
    return result


if __name__ == '__main__':  
    load_dotenv()
    # if unauthorized API is used, rate limit is lower leading to a ban and waiting time needs to be increased
    token = os.getenv('GITHUB_TOKEN') 
    api = GhApi(token = token)
    df_users = pd.read_csv("repository_collection/unique_users.csv")
    # drop students
    df_users = df_users.drop(df_users[df_users.is_student == True].index)

    result_repos = L()
    for user in df_users["github_user_id"]:
        print("Fetching repos for user: %s" % user)
        repos, requests = get_repos(api, user)
        if (repos is not None):
            repos_names = get_full_name_from_repos(repos)
            result_repos.extend(repos_names)
            print("Fetched repos: %s" % repos_names)
        else:
            print("User has no repositories.")
        time.sleep(requests*2)

    pd.Series(result_repos, name = "repositories").to_csv(Path("repository_collection", "repositories.csv"), index = False)