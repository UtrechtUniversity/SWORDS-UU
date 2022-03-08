"""
Tests for retrieval methods in user collection
"""
import pytest

from fastcore.foundation import L, AttrDict
from ghapi.all import GhApi, pages

from collect_users.methods.github_search.github_search import get_complete_query_result, get_users_from_repos, get_users_from_users


@pytest.fixture
def repos():
    repos = L(AttrDict(owner=AttrDict(login="kequach")), 
              AttrDict(owner=AttrDict(login="123")))

    return repos

@pytest.fixture
def users():
    users = L(AttrDict(login="kequach"), 
              AttrDict(login="123"))

    return users

def test_get_users_from_repos(repos):
    users_list = get_users_from_repos(repos)
    expected_result = ["kequach", "123"]

    actual_result = []
    for user in users_list:
        actual_result.append(user[2])

    assert expected_result == actual_result


def test_get_users_from_users(users):
    users_list = get_users_from_users(users)
    expected_result = ["kequach", "123"]

    actual_result = []
    for user in users_list:
        actual_result.append(user[2])

    assert expected_result == actual_result


def test_get_complete_query_result_repos(monkeypatch):
    def mock_get(url):
        return [AttrDict(total_count=2,
                          incomplete_results=False,
                          items=L(AttrDict(login="kequach"),
                                  AttrDict(login="kequach1")))]

    # api = GhApi()
    # monkeypatch.setattr(api.search, 'repos', mock_get)
    monkeypatch.setattr(GhApi.search, 'repos', mock_get)
    result = get_complete_query_result("test_query", "SEARCH_REPOS") 
    assert result[0]["items"]["login"] == "kequach"
