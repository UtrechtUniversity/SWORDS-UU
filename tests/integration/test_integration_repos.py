"""
Tests for retrieval methods in user collection
"""
import pytest

from ghapi.all import GhApi
import time

from collect_repositories.scripts.repositories import get_repos, get_repos_formatted, Service

"""
Tests for repositories.py
"""


@pytest.fixture
def service():
    return Service(api=GhApi())


def test_get_repos_from_users(service):
    df_users = ["asreview", "amices", "utrechtuniversity"]
    result_repos = []
    for user in df_users:
        repos = get_repos(user, service)
        if repos is not None:
            repos_formatted = get_repos_formatted(repos)
            result_repos.extend(repos_formatted)
        time.sleep(5)
    assert len(result_repos) >= 5
