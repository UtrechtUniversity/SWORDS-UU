"""
Retrieves howfairis variables for an input file of retrieved Github repositories.
"""
import os
import time
from datetime import datetime
import argparse

from howfairis import Repo, Checker
import pandas as pd
from dotenv import load_dotenv


def get_howfairis_compliance(url_repo):
    """Retrieve howfairis compliance - see https://github.com/fair-software/howfairis

    Args:
        url_repo (string): repository URL
    Returns:
        repository (bool): Whether repository is publicly accessible with version control
        license (bool): Whether repository has a license
        registry (bool): Whether code is in a registry
        citation (bool): Whether software is citable
        checklist (bool): Whether a software quality checklist is used
    """
    repo = Repo(url_repo)
    checker = Checker(repo, is_quiet=True)
    compliance = checker.check_five_recommendations()

    return (compliance.repository, compliance.license, compliance.registry,
            compliance.citation, compliance.checklist)


def read_input_file(file_path):
    """reads in the input file through Pandas

    Args:
        file_path (string): path to the file

    Returns:
        DataFrame
    """
    if "xlsx" in file_path:
        file = pd.read_excel(file_path, engine='openpyxl')
    else:
        file = pd.read_csv(file_path)
    return file


def parse_repo(repo_url):
    """Parses a repository for howfairis variables

    Args:
        repo_url (string): repository that should be parsed

    Returns:
        list: a list with the repository url and the variables
    """
    request_successful = False
    while not request_successful:
        try:
            entry = [repo_url]
            result = get_howfairis_compliance(repo_url)
            entry.extend(result)
            print(entry)
            time.sleep(2)
            request_successful = True
            return entry
        except Exception as e: # pylint: disable=broad-except
            print(f"Error occured for {repo_url} (most likely timeout issue due"
                f" to API limitation. Sleep for a while. Error message: {e}")
            if "Something went wrong asking the repo for its default branch" in str(
                    e):
                print("Skipping repository...")
                request_successful = True  # skip this repo
            elif "TimeoutError" in str(e):
                time.sleep(5)
            else:
                time.sleep(1500)

# if unauthorized API is used, rate limit is lower,
# leading to a ban and waiting time needs to be increased
# see: https://github.com/fair-software/howfairis/#rate-limit
load_dotenv()
token = os.getenv('GITHUB_TOKEN')
user = os.getenv('GITHUB_USER')
os.environ['APIKEY_GITHUB'] = user + ":" + token

if __name__ == '__main__':
    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument(
        "--input",
        "-i",
        help="The file name of the retrieved repositories.",
        default="../collect_repositories/results/repositories_filtered.csv")
    parser.add_argument("--output",
                        "-o",
                        help="The file name of the filtered repositories.",
                        default="results/repositories_howfairis.csv")

    # Read arguments from the command line
    args = parser.parse_args()
    print(f"Retrieving howfairis variables for the following file: {args.input}")



    df_repos = read_input_file(args.input)


    howfairis_variables = []

    for counter, url in enumerate(df_repos["html_url"]):
        howfairis_variables.append(parse_repo(url))
        if counter % 10 == 0:
            print(f"Parsed {counter} out of {len(df_repos.index)} repos.")

    df_howfairis = pd.DataFrame(howfairis_variables,
                                columns=[
                                    "html_url", "howfairis_repository",
                                    "howfairis_license", "howfairis_registry",
                                    "howfairis_citation", "howfairis_checklist"
                                ])
    df_repo_merged = pd.merge(df_repos, df_howfairis, how="left", on='html_url')

    current_date = datetime.today().strftime('%Y-%m-%d')
    df_repo_merged["date"] = current_date
    df_repo_merged.to_csv(args.output, index=False)

    print(
        f"Successfully retrieved howfairis variables for {len(df_howfairis.index)}"
        f" out of {len(df_repos.index)} repositories. Saved result to {args.output}."
    )
