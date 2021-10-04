from pathlib import Path
import argparse

from ghapi.all import GhApi, pages
from fastcore.foundation import L
import pandas as pd


def get_complete_query_result(api, query, query_type):
    # do first request to store last page variable in api object
    if (query_type == "SEARCH_REPOS"):
        api.search.repos(query, per_page=100)
        if (api.last_page() > 0):
            query_result = pages(api.search.repos, api.last_page(), query)
        else:
            # if there is only one page, last_page() will return 0. This will return nothing, so we need to use 1
            query_result = pages(api.search.repos, 1, query)
    elif (query_type == "SEARCH_USERS"):
        api.search.users(query, per_page=100)
        if (api.last_page() > 0):
            query_result = pages(api.search.users, api.last_page(), query)
        else:
            # if there is only one page, last_page() will return 0. This will return nothing, so we need to use 1
            query_result = pages(api.search.users, 1, query)
    result = L()
    for page in query_result:
        result.extend(page["items"])
    return result


def get_id_from_repos(repos):
    result = L()
    for repo in repos:
        result.append(repo["owner"]["login"])
    return result


def get_id_from_users(users):
    result = L()
    for user in users:
        result.append(user["login"])
    return result


# TODO: fix nondeterministic 403 error (see: https://github.com/fastai/ghapi/issues/44)
# main needs to be used since pages uses concurrency
if __name__ == '__main__':
    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument("--topic", "-t", help="set topic search string")
    parser.add_argument("--search", "-s", help="set general search string")

    # Read arguments from the command line
    args = parser.parse_args()
    
    api = GhApi()

    try:
        if(args.topic):
            print(f"Searching topics for {args.topic}...")
            topic_repos = get_complete_query_result(api, "topic:utrecht-university",
                                                    "SEARCH_REPOS")
            ids_topic_repos = get_id_from_repos(topic_repos)
            pd.Series(ids_topic_repos,
                    name="github_user_id").to_csv(Path("results",
                                                        "ids_topic_repos.csv"),
                                                    index=False)
            print("Searching topics done")
        else:
            print("No topic argument provided. If you want to retrieve topics, please provide the argument as --topic")

        if(args.search):
            print(f"Searching repos for {args.search}...")
            search_repos = get_complete_query_result(api, "utrecht university",
                                                    "SEARCH_REPOS")
            ids_search_repos = get_id_from_repos(search_repos)
            pd.Series(ids_search_repos,
                    name="github_user_id").to_csv(Path("results",
                                                        "ids_search_repos.csv"),
                                                    index=False)
            print("Searching repos done")

            print(f"Searching users for {args.search}...")
            search_users = get_complete_query_result(api, "utrecht university",
                                                    "SEARCH_USERS")
            ids_search_users = get_id_from_users(search_users)
            pd.Series(ids_search_users,
                    name="github_user_id").to_csv(Path("results",
                                                        "ids_search_users.csv"),
                                                    index=False)
            print("Searching users done")
        else:
            print("No search argument provided. If you want to retrieve general results and users, please provide the argument as --search")
    except Exception as e:
        print(f"Error occured: {e}")
        if("403" in str(e)):
            print("A HTTP Error 403 indicates that rate limits are reached. Please try again in a few minutes.")
