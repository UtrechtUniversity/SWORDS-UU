"""
Tests for retrieval methods in user collection
"""
import pytest
from unittest.mock import MagicMock, Mock
import os

from fastcore.foundation import L, AttrDict
from ghapi.all import GhApi

from collect_users.scripts.enrich_users import read_input_file, get_userdata, update_users 



"""
Tests for github_search.py
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


def test_get_users_from_repos(users_merged):
    def mock_get(*args, **kwargs):
        return AttrDict(login="kequach", 
                        id = 18238845,
                        node_id = "MDQ6VXNlcjE4MjM4ODQ1")

    print(users_merged)
    service = MagicMock()
    service.api.users.get_by_username.side_effect = mock_get
    usernames = users_merged["user_id"].head(3)
    result = get_userdata(usernames, service) 
    assert result["login"].values[0] == "kequach"


# def test_get_users_from_users(users, service):
#     users_list = get_users_from_users(users, service)
#     expected_result = ["kequach", "123"]

#     actual_result = []
#     for user in users_list:
#         actual_result.append(user[2])

#     assert expected_result == actual_result


# def test_get_complete_query_result_repos():
#     def mock_get(*args, **kwargs):
#         return AttrDict(total_count=2,
#                           incomplete_results=False,
#                           items=L(AttrDict(login="kequach"),
#                                   AttrDict(login="test_user2")))

#     service = MagicMock()
#     service.api.search.repos.side_effect = mock_get
#     service.api.last_page = Mock(return_value=0)
#     result = get_complete_query_result("test_query", "SEARCH_REPOS", service) 
#     assert result[0]["login"] == "kequach"


# """
# Tests for pure.py
# """

# @pytest.fixture
# def rispy_no_github():
#     rispy = {'type_of_reference': 'ADVS', 
#     'primary_title': 'ASReview Software Documentation.', 
#     'authors': ['de Bruin, J.', 'Ferdinands, G.', 'Harkema, A.', 'de Boer, J.', 'van den Brand, S.', 'Ma, Y.', 'van de Schoot, R.'], 
#     'year': '2021/1/18', 'publication_year': '2021/1/18', 
#     'doi': '10.5281/zenodo.4287119', 
#     'type_of_work': 'Software', 
#     'publisher': 'Zenodo'}
#     return rispy


# @pytest.fixture
# def rispy_github():
#     rispy = {'type_of_reference': 'ADVS', 
#     'primary_title': 'Birdwatcher', 
#     'secondary_authors': ['Mol, C.', 'ter Haar, Sita', 'Beckers, G.J.L.'], 
#     'year': '2018/11/30', 
#     'publication_year': '2018/11/30', 
#     'notes_abstract': 'Birdwatcher is a Python computer vision library for the analysis of animal behavior.It is developed by Gabriel Beckers, Sita ter Haar and Carien Mol, at Experimental Psychology, Utrecht University.It is being used in our lab but not stable enough yet for general use. More info will be provided when a first release is appropriate.Code can be found on GitHub: https://github.com/gbeckers/BirdwatcherIt is open source and freely available under the New BSD License terms.', 
#     'abstract': 'Birdwatcher is a Python computer vision library for the analysis of animal behavior.It is developed by Gabriel Beckers, Sita ter Haar and Carien Mol, at Experimental Psychology, Utrecht University.It is being used in our lab but not stable enough yet for general use. More info will be provided when a first release is appropriate.Code can be found on GitHub: https://github.com/gbeckers/BirdwatcherIt is open source and freely available under the New BSD License terms.', 
#     'type_of_work': 'Software'}
#     return rispy


# def test_get_username_from_text_empty(rispy_no_github):
#     user = get_username_from_text(rispy_no_github.values()) 
#     assert user is None


# def test_get_username_from_text_found(rispy_github):
#     user = get_username_from_text(rispy_github.values()) 
#     assert user == "gbeckers"