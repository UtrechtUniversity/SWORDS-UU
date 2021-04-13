from pathlib import Path

from ghapi.all import GhApi, pages
from fastcore.foundation import L
import pandas as pd

def get_complete_query_result(api, query, query_type):
    # do first request to store last page variable in api object
    if(query_type == "SEARCH_REPOS"):
        api.search.repos(query, per_page = 100)
        if(api.last_page() > 0):
            query_result = pages(api.search.repos, api.last_page(), query)
        else:
            # if 0 is used, query_result will be empty. This needs to be 1 in that case
            query_result = pages(api.search.repos, 1, query)
    elif(query_type == "SEARCH_USERS"):
        api.search.users(query, per_page = 100)
        if(api.last_page() > 0):
            query_result = pages(api.search.users, api.last_page(), query)
        else:
            # if 0 is used, query_result will be empty. This needs to be 1 in that case
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

    
# TODO: fix nondeterministic 403 error 
# main needs to be used since pages uses concurrency
if __name__ == '__main__':  
    api = GhApi()

    topic_repos = get_complete_query_result(api, "topic:utrecht-university", "SEARCH_REPOS")
    search_repos = get_complete_query_result(api, "utrecht university", "SEARCH_REPOS")
    search_users = get_complete_query_result(api, "utrecht university", "SEARCH_USERS")

    ids_topic_repos = get_id_from_repos(topic_repos)
    ids_search_repos = get_id_from_repos(search_repos)
    ids_search_users = get_id_from_users(search_users)

    pd.Series(ids_topic_repos).to_csv(Path("results", "ids_topic_repos.csv"), index = False)
    pd.Series(ids_search_repos).to_csv(Path("results", "ids_search_repos.csv"), index = False)
    pd.Series(ids_search_users).to_csv(Path("results", "ids_search_users.csv"), index = False)