import os
import time
from pathlib import Path

from howfairis import Repo, Checker
import pandas as pd
from dotenv import load_dotenv

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

# if unauthorized API is used, rate limit is lower leading to a ban and waiting time needs to be increased
# see: https://github.com/fair-software/howfairis/#rate-limit
load_dotenv()
token = os.getenv('GITHUB_TOKEN')
user = os.getenv('GITHUB_USER')
os.environ['APIKEY_GITHUB'] = user+":"+token


df_repos = pd.read_csv(Path("variable_collection", "repositories_filtered.csv"))
print(df_repos)

howfairis_variables = []
for counter, url in enumerate(df_repos["html_url"]):
    request_successful = False
    while(not request_successful):
        try:
            entry = [url]
            result = get_howfairis_compliance(url)
            entry.extend(result)
            print(entry)
            howfairis_variables.append(entry)
            if(counter % 10 == 0):
                print("Parsed %d repos." % counter)
            time.sleep(2)
            request_successful = True
        except Exception as e:
            print("Sleep for a while. Error message: %s" % str(e))
            time.sleep(1500)


df_howfairis = pd.DataFrame(howfairis_variables, columns=["html_url", "howfairis_repository", "howfairis_license", "howfairis_registry", "howfairis_citation", "howfairis_checklist"])

df_repo_merged = pd.merge(df_repos, df_howfairis, how="left", on='html_url')
df_repo_merged.to_csv(Path("variable_collection", "repositories_filtered.csv"), index=False)