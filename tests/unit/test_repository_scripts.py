"""
Tests for retrieval methods in user collection
"""
import pytest
from unittest.mock import MagicMock, Mock

from fastcore.foundation import AttrDict, L

from collect_repositories.scripts.repositories import get_repos, get_repos_formatted


@pytest.fixture
def mock_repos(*args, **kwargs):
    return L(AttrDict(name="MyAnimeList-Analysis", 
                    node_id = "MDEwOlJlcG9zaXRvcnkzMzgwNTU5MzQ=",
                    owner=AttrDict(login="kequach",
                                    id=18238845)),
            AttrDict(name="PrintXDKRequest", 
                    id = 440950736,
                    node_id = "MDEwOlJlcG9zaXRvcnkyMjg5ODc2OTQ=",
                    owner=AttrDict(login="kequach",
                                    id=18238845)))

"""
Tests for enrich_users.py
"""

def test_get_repos():
    def mock_get(*args, **kwargs):
        return L(AttrDict(name="MyAnimeList-Analysis", 
                        node_id = "MDEwOlJlcG9zaXRvcnkzMzgwNTU5MzQ=",
                        owner=AttrDict(login="kequach",
                                        id=18238845)),
                AttrDict(name="PrintXDKRequest", 
                        id = 440950736,
                        node_id = "MDEwOlJlcG9zaXRvcnkyMjg5ODc2OTQ=",
                        owner=AttrDict(login="kequach",
                                        id=18238845)))
    service = MagicMock()
    service.api.repos.list_for_user.side_effect = mock_get
    service.api.last_page = Mock(return_value=0)

    result = get_repos("kequach", service) 
    assert result[0]["name"] == "MyAnimeList-Analysis"

def test_get_repos_formatted(mock_repos):
    result = get_repos_formatted(mock_repos) 
    assert result[0]["name"] == "MyAnimeList-Analysis"