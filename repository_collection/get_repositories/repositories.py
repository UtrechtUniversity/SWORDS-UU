import os
import time
from pathlib import Path

from ghapi.all import GhApi, pages
from fastcore.foundation import L, AttrDict
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
        query_result = api.search.repos("user:" + user_id, per_page=100)
    except Exception as e:
        print("There was a problem with fetching repositories for user %s" % user_id)
        print(e)
        return (None, 1)
    requests = 1
    result = L()
    if(api.last_page() > 0):
        query_result = pages(
            api.search.repos, api.last_page(), "user:" + user_id)
        requests += 1
        for page in query_result:
            result.extend(page["items"])
    else:
        result.extend(query_result["items"])
    return (result, requests)


def get_repos_formatted(repos):
    """Goes through a list of repos and returns them correctly formatted

    Args:
        repos (L): fastcore foundation list of repositories

    Returns:
        L: fastcore founation list of complete repository data
    """
    result = L()
    for repo in repos:
        result.append(dict(repo))
    return result


if __name__ == '__main__':
    load_dotenv()
    # if unauthorized API is used, rate limit is lower leading to a ban and waiting time needs to be increased
    token = os.getenv('GITHUB_TOKEN')
    api = GhApi(token=token)
    df_users = pd.read_excel(Path("repository_collection", "unique_users_annotated.xlsx"), engine='openpyxl')
    # drop filtered users
    df_users = df_users.drop(df_users[df_users.final_decision == 0].index)
    df_users
    result_repos = []
    counter = 0
    for user in df_users["github_user_id"]:
        repos, requests = get_repos(api, user)
        if (repos is not None):
            repos_formatted = get_repos_formatted(repos)
            result_repos.extend(repos_formatted)
        else:
            print("User %s has no repositories." % user)
        time.sleep(requests*2 + .1)
        counter += 1
        if(counter % 10 == 0):
            print("Fetched %d users." % counter)

    # Flatten nested structures
    for i in range(len(result_repos)):
        for key in result_repos[i].keys():
            if(isinstance(result_repos[i][key], AttrDict)):
                print(key)
                if(key == "owner"):
                    result_repos[i][key] = result_repos[i][key]["login"]
                elif(key == "permissions"):
                    result_repos[i][key] = ""
                elif(key == "license"):
                    result_repos[i][key] = result_repos[i][key]["name"]

    df_result_repos = pd.DataFrame(result_repos)
    df_result_repos.to_csv(
        Path("repository_collection", "repositories.csv"), index=False)