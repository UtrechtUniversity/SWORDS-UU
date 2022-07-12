"""
Tests for retrieval methods in user collection
"""
import pytest

from ghapi.all import GhApi
import time
import pandas as pd

from collect_variables.scripts.github_api.github import (get_data_from_api,
                                                         Service,
                                                         Repo)

from collect_variables.scripts.howfairis_api.howfairis_variables import parse_repo


@pytest.fixture
def repo(*args, **kwargs):
    return Repo(repo_url="https://github.com/utrechtuniversity/swords-uu", repo_owner="utrechtuniversity", repo_repo_name="swords-uu", repo_branch="main")


@pytest.fixture
def repo_coc(*args, **kwargs):
    return Repo(repo_url="https://github.com/asreview/asreview", repo_owner="asreview", repo_repo_name="asreview", repo_branch="master")


@pytest.fixture
def service():
    return Service(api=GhApi(), sleep=10)


"""
Tests for howfairis_variables.py and github.py
"""


def test_get_howfairis_variables(repo):
    result = parse_repo(repo.url)
    time.sleep(10)
    assert len(result) == 6


def test_get_contributor_variables(repo, service):
    serv = service
    repository = repo
    retrieved_data = get_data_from_api(serv, repository, "contributors")
    assert len(retrieved_data[0]) == 20


def test_get_language_variables(repo, service):
    serv = service
    repository = repo
    # get_data_from_api(serv, repository, "contributors")
    retrieved_data = get_data_from_api(serv, repository, "languages")
    assert len(retrieved_data[0]) == 3


def test_get_readme(repo, service):
    serv = service
    repository = repo
    retrieved_data = get_data_from_api(serv, repository, "readmes")
    print(retrieved_data)
    assert "Scan and revieW of Open Research Data and Software" in retrieved_data[1]


def test_get_file_variables(repo, service):
    serv = service
    serv.file_list = ["readme"]
    repository = repo
    retrieved_data = get_data_from_api(serv, repository, "files")
    assert len(retrieved_data[0]) == 2


def test_get_test_variables(repo, service):
    serv = service
    repository = repo
    retrieved_data = get_data_from_api(serv, repository, "tests")
    assert len(retrieved_data[0]) == 2