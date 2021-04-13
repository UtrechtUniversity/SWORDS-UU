# TODO: Add github authentication due to expected large number of requests
from howfairis import Repo, Checker
def get_howfairis_compliance(url):
    """Retrieve howfairis compliance - see https://github.com/fair-software/howfairis

    Args:
        url (string): repository URL
    Returns:
        repository (bool): Whether repository is publicly accessible with version control
        license (bool): Whether repository has a license
        registry (bool): Whether code is in a registry
        citation (bool): Whether software is citable
        checklist (bool): Whether a software quality checklist is used
    """
    repo = Repo(url)
    checker = Checker(repo, is_quiet=True)
    compliance = checker.check_five_recommendations()
    
    return (compliance.repository, compliance.license, compliance.registry, compliance.citation, compliance.checklist)

print(get_howfairis_compliance("https://github.com/fair-software/howfairis"))