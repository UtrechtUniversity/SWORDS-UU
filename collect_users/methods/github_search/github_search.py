"""
This file retrieves Github usernames from the Github API
"""
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd
from fastcore.foundation import L
from ghapi.all import GhApi, pages


def get_complete_query_result(query, query_type):
    """Executes a search query and returns the result

    Args:
        query (string): The query to be executed
        query_type (string): Either SEARCH_REPOS to search repositories or
                             SEARCH_USERS to search users

    Returns:
        DataFrame: A dataframe with the results of the query
    """
    # do first request to store last page variable in api object
    if query_type == "SEARCH_REPOS":
        api.search.repos(query, per_page=100)
        if api.last_page() > 0:
            query_result = pages(api.search.repos, api.last_page(), query)
        else:
            # if there is only one page, last_page() will return 0.
            # This will return nothing, so we need to use 1
            query_result = pages(api.search.repos, 1, query)
    elif query_type == "SEARCH_USERS":
        api.search.users(query, per_page=100)
        if api.last_page() > 0:
            query_result = pages(api.search.users, api.last_page(), query)
        else:
            # if there is only one page, last_page() will return 0.
            # This will return nothing, so we need to use 1
            query_result = pages(api.search.users, 1, query)
    result = L()
    for page in query_result:
        result.extend(page["items"])
    return result


def get_users_from_repos(repos):
    """Retrieves the user from repositories data.

    Args:
        repos (DataFrame): Repositories retrieved from Github API

    Returns:
        L: list of users
    """
    result = L()
    for repo in repos:
        result.append([SERVICE, current_date, repo["owner"]["login"]])
    return result


def get_users_from_users(users):
    """Retrieves the user from users data.

    Args:
        users (DataFrame): Users retrieved from Github API

    Returns:
        L: list of users
    """
    result = L()
    for user in users:
        result.append([SERVICE, current_date, user["login"]])
    return result


if __name__ == '__main__':
    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument("--topic", "-t", help="set topic search string")
    parser.add_argument("--search", "-s", help="set general search string")

    # Read arguments from the command line
    args = parser.parse_args()

    api = GhApi()

    SERVICE = "github.com"
    current_date = datetime.today().strftime('%Y-%m-%d')
    columns = ["service", "date", "user_id"]
    try:
        if args.topic:
            print(f"Searching topics for {args.topic}...")
            topic_repos = get_complete_query_result(f"topic:{args.topic}",
                                                    "SEARCH_REPOS")
            ids_topic_repos = get_users_from_repos(topic_repos)
            pd.DataFrame(ids_topic_repos, columns=columns).to_csv(Path(
                "results", "github_search_topic.csv"),
                                                                  index=False)
            print("Searching topics done")
        else:
            print(
                "No topic argument provided. If you want to retrieve topics, "
                "please provide the argument as --topic")

        if args.search:
            print(f"Searching repos for {args.search}...")
            search_repos = get_complete_query_result(args.search,
                                                     "SEARCH_REPOS")
            ids_search_repos = get_users_from_repos(search_repos)
            pd.DataFrame(ids_search_repos, columns=columns).to_csv(Path(
                "results", "github_search_repos.csv"),
                                                                   index=False)
            print("Searching repos done")

            print(f"Searching users for {args.search}...")
            search_users = get_complete_query_result(args.search,
                                                     "SEARCH_USERS")
            ids_search_users = get_users_from_users(search_users)
            pd.DataFrame(ids_search_users, columns=columns).to_csv(Path(
                "results", "github_search_users.csv"),
                                                                   index=False)
            print("Searching users done")
        else:
            print(
                "No search argument provided. If you want to retrieve general results and "
                "users, please provide the argument as --search")
    except Exception as e: # pylint: disable=broad-except
        print(f"Error occured: {e}")
        if "403" in str(e):
            print("A HTTP Error 403 indicates that rate limits are reached. "
                  "Please try again in a few minutes.")
