"""
Tests for retrieval methods in user collection
"""
import pytest
from unittest.mock import MagicMock
import os

from fastcore.foundation import AttrDict

from collect_users.scripts.enrich_users import read_input_file, get_userdata, update_users 
from collect_users.scripts.prepare_filtering import is_student 




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


"""
Tests for enrich_users.py
"""

def test_get_userdata(users_merged):
    def mock_get(*args, **kwargs):
        return AttrDict(login="kequach", 
                        id = 18238845,
                        node_id = "MDQ6VXNlcjE4MjM4ODQ1")
    service = MagicMock()
    service.api.users.get_by_username.side_effect = mock_get
    usernames = users_merged["user_id"].head(1)
    result = get_userdata(usernames, service) 
    assert result["login"].values[0] == "kequach"


def test_update_users(users_enriched, users_enriched_old):
    users_enriched.rename({"user_id": "login"}, axis=1, inplace=True)
    result = update_users(users_enriched_old, users_enriched) 
    asreview_old = users_enriched_old.loc[users_enriched_old["user_id"] == "asreview"]
    asreview_new = result.loc[result["user_id"] == "asreview"]
    assert asreview_new["public_repos"].values[0] > asreview_old["public_repos"].values[0]


"""
Tests for prepare_filtering.py
"""

def test_is_student_true(users_enriched):
    student = users_enriched.loc[users_enriched["user_id"] == "altijd-youri"]
    is_student_result = is_student(student["bio"].values[0])
    assert is_student_result == True


def test_is_student_false(users_enriched):
    not_student = users_enriched.loc[users_enriched["user_id"] == "asreview"]
    is_student_result = is_student(not_student["bio"].values[0])
    assert is_student_result == False
    