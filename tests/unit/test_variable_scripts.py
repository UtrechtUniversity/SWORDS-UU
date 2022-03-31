"""
Tests for methods in variable collection
"""
import pytest
from unittest.mock import MagicMock

from fastcore.foundation import AttrDict, L
from howfairis import Compliance

from collect_variables.scripts.github_api.github import (get_data_from_api,
                                                         get_coc,
                                                         get_contributors,
                                                         get_jupyter_notebooks,
                                                         get_languages,
                                                         get_readmes,
                                                         Repo)

from collect_variables.scripts.howfairis_api.howfairis_variables import (get_howfairis_compliance,
                                                                         parse_repo)


@pytest.fixture
def mock_repo(*args, **kwargs):
    return Repo(repo_url="https://github.com/asreview/asreview-covid19", repo_owner="asreview", repo_repo_name="asreview-covid19", repo_branch="main")


"""
Tests for howfairis.py
"""


def test_parse_repo(mock_repo, monkeypatch):
    def mock_get(*args, **kwargs):
        return (True, True, True, True, False)
    monkeypatch.setattr(
        "collect_variables.scripts.howfairis_api.howfairis_variables.get_howfairis_compliance", mock_get)

    result = parse_repo(mock_repo.url)
    assert "asreview-covid19" in result[0] and True == result[1] 


def test_get_howfairis_compliance(mock_repo, monkeypatch):
    def mock_get(*args, **kwargs):
        return Compliance(repository=True,
                          license_=True,
                          registry=True,
                          citation=True,
                          checklist=False)
    monkeypatch.setattr(
        "howfairis.Checker.check_five_recommendations", mock_get)

    result = get_howfairis_compliance(mock_repo.url)
    assert True == result[1] 


"""
Compliance(repository=self.check_repository(),
                          license_=self.check_license(),
                          registry=self.check_registry(),
                          citation=self.check_citation(),
                          checklist=self.check_checklist())
                          
"""

"""
Tests for github.py
"""


def test_get_data_from_api(mock_repo):
    def mock_get(*args, **kwargs):
        return AttrDict(url="https://api.github.com/repos/kequach/MyAnimeList-Analysis/git/trees/ef0ab1f473fea05a46ffdafdf08a4acf6ddfa6f4",
                        tree=L(AttrDict(path="README.md",
                                        type="blob"),
                               AttrDict(path="code_of_conduct.md",
                                        type="blob")))

    service = MagicMock()
    service.api.git.get_tree.side_effect = mock_get

    result = get_data_from_api(service, mock_repo, "coc")
    assert result[1] == "code_of_conduct.md"


def test_get_coc(mock_repo):
    def mock_get(*args, **kwargs):
        return AttrDict(url="https://api.github.com/repos/kequach/MyAnimeList-Analysis/git/trees/ef0ab1f473fea05a46ffdafdf08a4acf6ddfa6f4",
                        tree=L(AttrDict(path="README.md",
                                        type="blob"),
                               AttrDict(path="code_of_conduct.md",
                                        type="blob")))

    service = MagicMock()
    service.api.git.get_tree.side_effect = mock_get

    result = get_coc(service, mock_repo)
    assert result[1] == "code_of_conduct.md"


def test_get_contributors(mock_repo):
    def mock_get(*args, **kwargs):
        return L(AttrDict(login="kequach", contributions=150),
                 AttrDict(login="chrisslewe", contributions=100),
                 AttrDict(login="J535D165", contributions=200))

    service = MagicMock()
    service.api.repos.list_contributors = mock_get

    result = get_contributors(service, mock_repo)
    assert result[0][1] == "kequach"


def test_get_jupyter_notebooks(mock_repo):
    def mock_get(*args, **kwargs):
        return AttrDict(url="https://api.github.com/repos/kequach/MyAnimeList-Analysis/git/trees/ef0ab1f473fea05a46ffdafdf08a4acf6ddfa6f4",
                        tree=L(AttrDict(path="README.md",
                                        type="blob"),
                               AttrDict(path="analysis_notebook.ipynb",
                                        type="blob")))

    service = MagicMock()
    service.api.git.get_tree.side_effect = mock_get

    result = get_jupyter_notebooks(service, mock_repo)
    assert result[0][1] == "analysis_notebook.ipynb"


def test_get_languages(mock_repo):
    def mock_get(*args, **kwargs):
        return AttrDict(Python=1337, Shell=420)

    service = MagicMock()
    service.api.repos.list_languages = mock_get

    result = get_languages(service, mock_repo)
    assert result[0][1] == "Python"


def test_get_readmes(mock_repo):
    def mock_get(*args, **kwargs):
        return AttrDict(name="readme.md", content=r"""
IVtBU1JldmlldyBmb3IgQ09WSUQxOV0oaHR0cHM6Ly9naXRodWIuY29tL2Fz
cmV2aWV3L2FzcmV2aWV3L2Jsb2IvbWFzdGVyL2ltYWdlcy9pbnRyby1jb3Zp
ZDE5LXNtYWxsLnBuZz9yYXc9dHJ1ZSkKCkV4dGVuc2lvbiB0byBhZGQgcHVi
bGljYXRpb25zIG9uIENPVklELTE5IHRvIFtBU1Jldmlld10oaHR0cHM6Ly9n
aXRodWIuY29tL2FzcmV2aWV3L2FzcmV2aWV3KS4KCiMgQVNSZXZpZXcgYWdh
aW5zdCBDT1ZJRC0xOQoKWyFbRG93bmxvYWRzXShodHRwczovL3BlcHkudGVj
aC9iYWRnZS9hc3Jldmlldy1jb3ZpZDE5KV0oaHR0cHM6Ly9wZXB5LnRlY2gv
cHJvamVjdC9hc3Jldmlldy1jb3ZpZDE5KSBbIVtQeVBJIHZlcnNpb25dKGh0
dHBzOi8vYmFkZ2UuZnVyeS5pby9weS9hc3Jldmlldy1jb3ZpZDE5LnN2Zyld
KGh0dHBzOi8vYmFkZ2UuZnVyeS5pby9weS9hc3Jldmlldy1jb3ZpZDE5KSBb
IVtET0ldKGh0dHBzOi8vemVub2RvLm9yZy9iYWRnZS9ET0kvMTAuNTI4MS96
ZW5vZG8uMzc2NDc0OS5zdmcpXShodHRwczovL2RvaS5vcmcvMTAuNTI4MS96
ZW5vZG8uMzc2NDc0OSkgWyFbTGljZW5zZV0oaHR0cHM6Ly9pbWcuc2hpZWxk
cy5pby9iYWRnZS9MaWNlbnNlLUFwYWNoZSUyMDIuMC1ibHVlLnN2ZyldKGh0
dHBzOi8vb3BlbnNvdXJjZS5vcmcvbGljZW5zZXMvQXBhY2hlLTIuMCkKClRo
ZSBBY3RpdmUgbGVhcm5pbmcgZm9yIFN5c3RlbWF0aWMgUmV2aWV3cyBzb2Z0
d2FyZSBbQVNSZXZpZXddKGh0dHBzOi8vZ2l0aHViLmNvbS9hc3Jldmlldy9h
c3JldmlldykgaW1wbGVtZW50cyBsZWFybmluZyBhbGdvcml0aG1zIHRoYXQg
aW50ZXJhY3RpdmVseSBxdWVyeSB0aGUgcmVzZWFyY2hlciBkdXJpbmcgdGhl
IHRpdGxlIGFuZCBhYnN0cmFjdCByZWFkaW5nIHBoYXNlIG9mIGEgc3lzdGVt
YXRpYyBzZWFyY2guIFRoaXMgd2F5IG9mIGludGVyYWN0aXZlIHRyYWluaW5n
IGlzIGtub3duIGFzIGFjdGl2ZSBsZWFybmluZy4gQVNSZXZpZXcgb2ZmZXJz
IHN1cHBvcnQgZm9yIGNsYXNzaWNhbCBsZWFybmluZyBhbGdvcml0aG1zIGFu
ZCBzdGF0ZS1vZi10aGUtYXJ0IGxlYXJuaW5nIGFsZ29yaXRobXMgbGlrZSBu
ZXVyYWwgbmV0d29ya3MuIFRoZSBzb2Z0d2FyZSBjYW4gYmUgdXNlZCBmb3Ig
dHJhZGl0aW9uYWwgc3lzdGVtYXRpYyByZXZpZXdzIGZvciB3aGljaCB0aGUg
dXNlciB1cGxvYWRzIGEgZGF0YXNldCBvZiBwYXBlcnMsIG9yIG9uZSBjYW4g
bWFrZSB1c2Ugb2YgdGhlIGJ1aWx0LWluIGRhdGFzZXRzLgoKVG8gaGVscCBj
b21iYXQgdGhlIENPVklELTE5IGNyaXNpcywgdGhlIEFTUmV2aWV3IHRlYW0g
cmVsZWFzZWQgYW4gZXh0ZW5zaW9uIHRoYXQgaW50ZWdyYXRlcyB0aGUgbGF0
ZXN0IHNjaWVudGlmaWMgZGF0YXNldHMgb24gQ09WSUQtMTkgaW4gdGhlIEFT
UmV2aWV3IHNvZnR3YXJlLiBFeHBlcnRzIGNhbiAqKnN0YXJ0IHJldmlld2lu
ZyB0aGUgbGF0ZXN0IHNjaWVudGlmaWMgbGl0ZXJhdHVyZSBvbiBDT1ZJRC0x
OSBpbW1lZGlhdGVseSEqKiBTZWUgW2RhdGFzZXRzXSgjZGF0YXNldHMpIGZv
ciBhbiBvdmVydmlldyBvZiB0aGUgZGF0YXNldHMgKGRhaWx5IHVwZGF0ZXMp
LgoKCiMjIEluc3RhbGxhdGlvbiwgdXBkYXRlLCBhbmQgdXNhZ2UKClRoZSBD
T1ZJRC0xOSBwbHVnLWluIHJlcXVpcmVzIEFTUmV2aWV3IDAuOS40IG9yIGhp
Z2hlci4gSW5zdGFsbCBBU1JldmlldyBieSBmb2xsb3dpbmcgdGhlIGluc3Ry
dWN0aW9ucyBpbiBbSW5zdGFsbGF0aW9uIG9mIEFTUmV2aWV3XShodHRwczov
L2FzcmV2aWV3LnJlYWR0aGVkb2NzLmlvL2VuL2xhdGVzdC9pbnN0YWxsYXRp
b24uaHRtbCkuCgpJbnN0YWxsIHRoZSBleHRlbnNpb24gd2l0aCBwaXA6Cgpg
YGBiYXNoCnBpcCBpbnN0YWxsIGFzcmV2aWV3LWNvdmlkMTkKYGBgCgpUaGUg
ZGF0YXNldHMgYXJlIGltbWVkaWF0ZWx5IGF2YWlsYWJsZSBhZnRlciBzdGFy
dGluZyBBU1JldmlldyAoYGFzcmV2aWV3IG9yYWNsZWApLiBUaGUgZGF0YXNl
dHMgYXJlIHNlbGVjdGFibGUgaW4gU3RlcCAyIG9mIHRoZSBwcm9qZWN0IGlu
aXRpYWxpemF0aW9uLiBGb3IgbW9yZSBpbmZvcm1hdGlvbiBvbiB0aGUgdXNh
Z2Ugb2YgQVNSZXZpZXcsIHBsZWFzZSBoYXZlIGEgbG9vayBhdCB0aGUgW1F1
aWNrIFRvdXJdKGh0dHBzOi8vYXNyZXZpZXcucmVhZHRoZWRvY3MuaW8vZW4v
bGF0ZXN0L3F1aWNrdG91ci5odG1sKS4KCk9sZGVyIHZlcnNpb25zIG9mIHRo
ZSBwbHVnaW4gYXJlIG5vIGxvbmdlciBzdXBwb3J0ZWQgYnkgQVNSZXZpZXc+
PTAuOS40LiBQbGVhc2UgdXBkYXRlIHRoZSBwbHVnaW4gd2l0aDogCgpgYGBi
YXNoCnBpcCBpbnN0YWxsIC0tdXBncmFkZSBhc3Jldmlldy1jb3ZpZDE5CmBg
YAoKCiMjIERhdGFzZXRzCgpUaGUgZm9sbG93aW5nIGRhdGFzZXRzIGFyZSBh
dmFpbGFibGU6CgotIFtDT1JELTE5IGRhdGFzZXRdKCNjb3JkLTE5LWRhdGFz
ZXQpCi0gW0NPVklEMTkgcHJlcHJpbnRzIGRhdGFzZXRdKCNjb3ZpZDE5LXBy
ZXByaW50cy1kYXRhc2V0KQoKOmV4Y2xhbWF0aW9uOiBUaGUgZGF0YXNldHMg
YXJlIGNoZWNrZWQgZm9yIHVwZGF0ZXMgZXZlcnkgY291cGxlIG9mIGhvdXJz
IHN1Y2ggdGhhdCB0aGUgbGF0ZXN0IGNvbGxlY3Rpb25zIGFyZSBhdmFpbGFi
bGUgaW4gdGhlIEFTUmV2aWV3IENPVklEMTkgcGx1Z2luIGFuZCBBU1Jldmll
dyBzb2Z0d2FyZS4KClshW0FTUmV2aWV3IENPUkQxOSBkYXRhc2V0c10oaHR0
cHM6Ly9naXRodWIuY29tL2FzcmV2aWV3L2FzcmV2aWV3L2Jsb2IvbWFzdGVy
L2RvY3MvaW1hZ2VzL2FzcmV2aWV3LWNvdmlkMTktc2NyZWVuc2hvdC5wbmc/
cmF3PXRydWUpXShodHRwczovL2dpdGh1Yi5jb20vYXNyZXZpZXcvYXNyZXZp
ZXctY292aWQxOSkKCiMjIyBDT1JELTE5IGRhdGFzZXQKVGhlIFtDT1JELTE5
IGRhdGFzZXRdKGh0dHBzOi8vcGFnZXMuc2VtYW50aWNzY2hvbGFyLm9yZy9j
b3JvbmF2aXJ1cy1yZXNlYXJjaCkgaXMgYSBkYXRhc2V0IHdpdGggc2NpZW50
aWZpYyBwdWJsaWNhdGlvbnMgb24gQ09WSUQtMTkgYW5kIGNvcm9uYXZpcnVz
LXJlbGF0ZWQgcmVzZWFyY2ggKGUuZy4gU0FSUywgTUVSUywgZXRjLikgZnJv
bSBQdWJNZWQgQ2VudHJhbCwgdGhlIFdITyBDT1ZJRC0xOSBkYXRhYmFzZSBv
ZiBwdWJsaWNhdGlvbnMsIHRoZSBwcmVwcmludCBzZXJ2ZXJzIGJpb1J4aXYs
IG1lZFJ4aXYgYW5kIGFyWGl2LCBhbmQgcGFwZXJzIGNvbnRyaWJ1dGVkIGJ5
IHNwZWNpZmljIHB1Ymxpc2hlcnMgKGN1cnJlbnRseSBFbHNldmllcikuIFRo
ZSBkYXRhc2V0IGlzIGNvbXBpbGVkIGFuZCBtYWludGFpbmVkIGJ5IGEgY29s
bGFib3JhdGlvbiBvZiB0aGUgQWxsZW4gSW5zdGl0dXRlIGZvciBBSSwgdGhl
IENoYW4gWnVja2VyYmVyZyBJbml0aWF0aXZlLCBHZW9yZ2V0b3duIFVuaXZl
cnNpdHnigJlzIENlbnRlciBmb3IgU2VjdXJpdHkgYW5kIEVtZXJnaW5nIFRl
Y2hub2xvZ3ksIE1pY3Jvc29mdCBSZXNlYXJjaCwgYW5kIHRoZSBOYXRpb25h
bCBMaWJyYXJ5IG9mIE1lZGljaW5lIG9mIHRoZSBOYXRpb25hbCBJbnN0aXR1
dGVzIG9mIEhlYWx0aC4gVGhlIGZ1bGwgZGF0YXNldCBjb250YWlucyBtZXRh
ZGF0YSBvZiBtb3JlIHRoYW4gKioxMDBLIHB1YmxpY2F0aW9ucyoqIG9uIENP
VklELTE5IGFuZCBjb3JvbmF2aXJ1cy1yZWxhdGVkIHJlc2VhcmNoLiAqKlRo
ZSBDT1JELTE5IGRhdGFzZXQgcmVjZWl2ZXMgZGFpbHkgdXBkYXRlcyBhbmQg
aXMgZGlyZWN0bHkgYXZhaWxhYmxlIGluIHRoZSBBU1JldmlldyBzb2Z0d2Fy
ZS4qKiBUaGUgbW9zdCByZWNlbnQgdmVyc2lvbnMgb2YgdGhlIGRhdGFzZXQg
Y2FuIGJlIGZvdW5kIGhlcmU6IGh0dHBzOi8vYWkyLXNlbWFudGljc2Nob2xh
ci1jb3JkLTE5LnMzLXVzLXdlc3QtMi5hbWF6b25hd3MuY29tL2hpc3Rvcmlj
YWxfcmVsZWFzZXMuaHRtbAoKIyMjIENPVklEMTkgcHJlcHJpbnRzIGRhdGFz
ZXQKVGhlIFtDT1ZJRDE5IHByZXByaW50cyBkYXRhc2V0XShodHRwczovL2dp
dGh1Yi5jb20vbmljaG9sYXNtZnJhc2VyL2NvdmlkMTlfcHJlcHJpbnRzKSBp
cyBjcmVhdGVkIGJ5IFtOaWNob2xhcyBGcmFzZXJdKGh0dHBzOi8vZ2l0aHVi
LmNvbS9uaWNob2xhc21mcmFzZXIpIGFuZCBbQmlhbmNhIEtyYW1lcl0oaHR0
cHM6Ly9naXRodWIuY29tL2Jta3JhbWVyKSwgYnkgY29sbGVjdGluZyBtZXRh
ZGF0YSBvZiBDT1ZJRDE5LXJlbGF0ZWQgcHJlcHJpbnRzIGZyb20gb3ZlciAx
NSBwcmVwcmludCBzZXJ2ZXJzIHdpdGggRE9JcyByZWdpc3RlcmVkIHdpdGgg
Q3Jvc3NyZWYgb3IgRGF0YUNpdGUsIGFuZCBmcm9tIGFyWGl2LiBUaGUgZGF0
YXNldCBjb250YWlucyBtZXRhZGF0YSBvZiA+MTBLIHByZXByaW50cyBvbiBD
T1ZJRC0xOSBhbmQgY29yb25hdmlydXMtcmVsYXRlZCByZXNlYXJjaC4gQWxs
IHZlcnNpb25zIGFyZSBhcmNoaXZlZCBvbiBbRmlnc2hhcmVdKGh0dHBzOi8v
ZG9pLm9yZy8xMC42MDg0L205LmZpZ3NoYXJlLjEyMDMzNjcyKS4gVGhlIENP
VklEMTkgcHJlcHJpbnRzIGRhdGFzZXQgcmVjZWl2ZXMgd2Vla2x5IHVwZGF0
ZXMuCgpUaGUgbW9zdCByZWNlbnQgdmVyc2lvbiBvZiB0aGUgZGF0YXNldCBj
YW4gYmUgZm91bmQgaGVyZTpbaHR0cHM6Ly9naXRodWIuY29tL25pY2hvbGFz
bWZyYXNlci9jb3ZpZDE5X3ByZXByaW50cy9ibG9iL21hc3Rlci9kYXRhL2Nv
dmlkMTlfcHJlcHJpbnRzLmNzdl0oaHR0cHM6Ly9naXRodWIuY29tL25pY2hv
bGFzbWZyYXNlci9jb3ZpZDE5X3ByZXByaW50cy9ibG9iL21hc3Rlci9kYXRh
L2NvdmlkMTlfcHJlcHJpbnRzLmNzdikuCgojIyBMaWNlbnNlLCBjaXRhdGlv
biBhbmQgY29udGFjdAoKVGhlIEFTUmV2aWV3IHNvZnR3YXJlIGFuZCB0aGUg
cGx1Z2luIGhhdmUgYW4gQXBhY2hlIDIuMCBMSUNFTlNFLiBGb3IgdGhlIGRh
dGFzZXRzLCBwbGVhc2Ugc2VlIHRoZSBsaWNlbnNlIG9mIHRoZSBDT1JELTE5
IGRhdGFzZXQgaHR0cHM6Ly9wYWdlcy5zZW1hbnRpY3NjaG9sYXIub3JnL2Nv
cm9uYXZpcnVzLXJlc2VhcmNoLiBUaGUgQ09WSUQxOSBwcmVwcmludHMgZGF0
YXNldCBoYXMgYSBbQ0MwIGxpY2Vuc2VdKGh0dHBzOi8vY3JlYXRpdmVjb21t
b25zLm9yZy9wdWJsaWNkb21haW4vemVyby8xLjAvKS4KClZpc2l0IGh0dHBz
Oi8vZG9pLm9yZy8xMC41MjgxL3plbm9kby4zNzY0NzQ5IHRvIGdldCB0aGUg
Y2l0YXRpb24gc3R5bGUgb2YgeW91ciBwcmVmZXJlbmNlLgoKVGhpcyBwcm9q
ZWN0IGlzIGNvb3JkaW5hdGVkIGJ5IGJ5IFJlbnMgdmFuIGRlIFNjaG9vdCAo
QFJlbnN2YW5kZXNjaG9vdCkgYW5kIERhbmllbCBPYmVyc2tpIChAZGFvYikg
YW5kIGlzIHBhcnQgb2YgdGhlIHJlc2VhcmNoIHdvcmsgY29uZHVjdGVkIGJ5
cmVjaHQgVW5pdmVyc2l0eSwgVGhlIE5ldGhlcmxhbmRzLiBNYWludGFpbmVy
cyBhcmUgSm9uYXRoYW4gZGUgQnJ1aW4gKEBKNTM1RDE2NSkgYW5kIFJhb3Vs
IFNjaHJhbSAoQHF1Yml4ZXMpLgoKR290IGlkZWFzIGZvciBpbXByb3ZlbWVu
dD8gRm9yIGFueSBxdWVzdGlvbnMgb3IgcmVtYXJrcywgcGxlYXNlIHNlbmQg
YW4gZW1haWwgdG8gYXNyZXZpZXdAdXUubmwuCg==
""")

    service = MagicMock()
    service.api.repos.get_readme = mock_get

    result = get_readmes(service, mock_repo)
    assert "[ASReview for COVID19]" in result[1]
