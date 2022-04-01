"""
Tests for retrieval methods in user collection
"""
import pytest

from ghapi.all import GhApi
import os
import pandas as pd
import time

from collect_users.methods.github_search.github_search import get_complete_query_result, get_users_from_repos, get_users_from_users
from collect_users.scripts.enrich_users import read_input_file, get_userdata, update_users, Service
from collect_users.scripts.prepare_filtering import is_student

"""
Tests for github_search.py
"""


@pytest.fixture
def service():
    return Service(api=GhApi(), sleep=10)


def test_search_topics(service):
    topic_repos = get_complete_query_result(
        f"topic:utrecht-university", "SEARCH_REPOS", service)
    ids_topic_repos = get_users_from_repos(topic_repos, service)
    time.sleep(5)
    assert len(ids_topic_repos[0]
               ) == 3 and ids_topic_repos[0][0] == "github.com"


def test_search_users(service):
    search_users = get_complete_query_result(
        "utrecht university", "SEARCH_USERS", service)
    ids_search_users = get_users_from_users(search_users, service)
    time.sleep(5)
    assert len(ids_search_users[0]
               ) == 3 and ids_search_users[0][0] == "github.com"


"""
Tests for user collection scripts
"""


@pytest.fixture
def path():
    return os.path.dirname(__file__)


@pytest.fixture
def users_merged(path):
    return read_input_file(os.path.join(path, "test_data/users_merged.csv"))


@pytest.fixture
def users_enriched(path):
    return read_input_file(os.path.join(path, "test_data/users_enriched.xlsx"))


@pytest.fixture
def users_enriched_old(path):
    return read_input_file(os.path.join(path, "test_data/users_enriched_summer2021.xlsx"))


def test_enrich_new_users(users_merged, service):
    results_github_user_api = get_userdata(
        users_merged.head(3)["user_id"], service)
    results_github_user_api["login"] = results_github_user_api["login"].str.lower(
    )
    # key to merge is lowercase so this needs to be lowercase as well
    df_users_enriched = users_merged.merge(results_github_user_api,
                                           left_on="user_id",
                                           right_on="login",
                                           how="left")
    df_users_enriched.drop(["login"], axis=1, inplace=True)
    # is there at least one id that is not NaN? Then the script works as intended (accounts may be deleted over time)
    assert df_users_enriched["id"].isnull().all() == False


def test_update_new_users(users_enriched_old, users_merged, service):
    df_users_annotated = users_enriched_old
    df_users = users_merged
    df_users = df_users.drop_duplicates("user_id").reset_index(drop=True)

    df_users["new_user"] = False
    df_users.loc[~df_users["user_id"].isin(
        df_users_annotated["user_id"].str.lower()), "new_user"] = True

    df_users_update = pd.merge(df_users[df_users["new_user"]],
                               df_users_annotated,
                               left_on="user_id",
                               right_on="user_id",
                               how="left")
    results_github_user_api = get_userdata(
        df_users_update.head(2)["user_id"], service)

    df_users_enriched = update_users(df_users_annotated,
                                     results_github_user_api)
    assert len(df_users_enriched) >= len(df_users_annotated)


def test_filter_users(users_enriched):
    df_users_enriched = users_enriched
    df_users_enriched["is_student"] = df_users_enriched['bio'].apply(
        is_student)
    assert df_users_enriched['is_student'].value_counts()[1] == 117
