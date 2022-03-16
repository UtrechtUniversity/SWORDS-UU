"""
Tests for retrieval methods in user collection
"""
import pytest
from unittest.mock import MagicMock, Mock

from fastcore.foundation import L, AttrDict
from ghapi.all import GhApi

from collect_users.methods.github_search.github_search import get_complete_query_result, get_users_from_repos, get_users_from_users, Service

@pytest.fixture
def service():
    return Service(api=GhApi())

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

def test_get_users_from_repos(repos, service):
    users_list = get_users_from_repos(repos, service)
    expected_result = ["kequach", "123"]

    actual_result = []
    for user in users_list:
        actual_result.append(user[2])

    assert expected_result == actual_result


def test_get_users_from_users(users, service):
    users_list = get_users_from_users(users, service)
    expected_result = ["kequach", "123"]

    actual_result = []
    for user in users_list:
        actual_result.append(user[2])

    assert expected_result == actual_result


def test_get_complete_query_result_repos():
    def mock_get(*args, **kwargs):
        return AttrDict(total_count=2,
                          incomplete_results=False,
                          items=L(AttrDict(login="kequach"),
                                  AttrDict(login="test_user2")))

    service = MagicMock()
    service.api.search.repos.side_effect = mock_get
    service.api.last_page = Mock(return_value=0)
    result = get_complete_query_result("test_query", "SEARCH_REPOS", service) 
    assert result[0]["login"] == "kequach"
