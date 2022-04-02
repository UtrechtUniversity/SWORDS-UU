"""
This file retrieves Github API variables for an input file with repositories.
"""
import os
import sys
import time
from datetime import datetime
import ast
import argparse
import base64

import pandas as pd
from dotenv import load_dotenv
from ghapi.all import GhApi
from fastcore.foundation import L


class Service:
    """
    Common variables used in functions bundled in Service class.
    """

    def __init__(self, api: GhApi, sleep=6):
        self.api = api
        self.current_date = datetime.today().strftime('%Y-%m-%d')
        self.sleep = sleep


class Repo:
    """
    Repository variables bundled together.

    url (string): repository url.
        E.g.: https://api.github.com/repos/kequach/HTML-Examples/contributors
    owner (string): repository owner. E.g.: kequach
    repo_name (string): repository name. E.g.: HTML-Examples
    branch (string): repository default branch. E.g.: main / master
    """

    def __init__(self, repo_url, repo_owner, repo_repo_name, repo_branch="main"):
        self.url = repo_url
        self.owner = repo_owner
        self.repo_name = repo_repo_name
        self.branch = repo_branch


def read_input_file(file_path):
    """reads in the input file through Pandas

    Args:
        file_path (string): path to the file

    Returns:
        DataFrame
    """
    if "xlsx" in file_path:
        input_file = pd.read_excel(file_path, engine='openpyxl')
    else:
        input_file = pd.read_csv(file_path)
    return input_file


def export_file(variables_retrieved, columns, var_type, output):
    """Exports the retrieved data to a file.

    Args:
        variables_retrieved (List): Holds the retrieved variables
        columns (List): column names of the retrieved variables
        var_type (string): Used to output which variables were retrieved
        output (string): file path
    """
    df_data = pd.DataFrame(variables_retrieved, columns=columns)
    current_date = datetime.today().strftime('%Y-%m-%d')
    df_data["date"] = current_date
    df_data.to_csv(output, index=False)
    print(
        f"Successfully retrieved {var_type} variables. Saved result to {output}."
    )


def get_contributors(service: Service, repo: Repo, verbose=True):
    """Retrieves contributors for a Github repository

    Args:
        service (Service): Service object with API connection and metadata vars
        repo    (Repo)   : Repository variables bundled together
        verbose (boolean): if True, retrieve all variables from API.
                           Otherwise, only collect username and contributions

    Returns:
        list: contributors list retrieved from Github
    """
    contributors = []
    contributors_data = service.api.repos.list_contributors(
        owner=repo.owner, repo=repo.repo_name, anon=0, per_page=100)
    for contributor in contributors_data:
        entry = [repo.url]
        if verbose:
            entry.extend(list(contributor.values()))
        else:
            entry.extend([contributor.get("login"),
                         contributor.get("contributions")])
        print(entry[0:2])
        contributors.append(entry)

    return contributors


def get_languages(service: Service, repo: Repo):
    """Retrieves languages for a Github repository

    Args:
        service (Service): Service object with API connection and metadata vars
        repo    (Repo)   : Repository variables bundled together

    Returns:
        list: languages list retrieved from Github
    """
    languages = []
    languages_data = service.api.repos.list_languages(
        owner=repo.owner, repo=repo.repo_name)
    for language, num_chars in languages_data.items():
        languages_entry = [repo.url]
        languages_entry.extend([language, num_chars])
        print(languages_entry)
        languages.append(languages_entry)
    return languages


def get_jupyter_notebooks(service: Service, repo: Repo):
    """Retrieves jupyter notebooks for a Github repository

    Args:
        service (Service): Service object with API connection and metadata vars
        repo    (Repo)   : Repository variables bundled together

    Returns:
        list: jupyter notebooks file name list retrieved from Github
    """
    jupyter_notebooks = []
    jupyter_notebooks_data = service.api.git.get_tree(
        owner=repo.owner, repo=repo.repo_name,
        tree_sha=repo.branch, recursive=1)
    for file in jupyter_notebooks_data["tree"]:
        if file["type"] == "blob" and ".ipynb" in file["path"]:
            jupyter_notebooks_entry = [repo.url, file["path"]]
            print(jupyter_notebooks_entry)
            jupyter_notebooks.append(jupyter_notebooks_entry)
    return jupyter_notebooks


def get_readmes(service: Service, repo: Repo):
    """Retrieves languages for a Github repository

    Args:
        service (Service): Service object with API connection and metadata vars
        repo    (Repo)   : Repository variables bundled together

    Returns:
        string: readme retrieved from Github
    """
    readme = base64.b64decode(service.api.repos.get_readme(
        repo.owner, repo.repo_name).content)

    readme_data = [repo.url, readme.decode()]
    return readme_data


def get_coc(service: Service, repo: Repo):
    """Retrieves code of conduct file locations for a Github repository.
    There are also functions to retrieve a code of conduct in ghapi but they seem deprecated.

    Args:
        service (Service): Service object with API connection and metadata vars
        repo    (Repo)   : Repository variables bundled together

    Returns:
        string: code of conduct retrieved from Github
    """
    coc = []
    content = service.api.git.get_tree(owner=repo.owner, repo=repo.repo_name,
                                       tree_sha=repo.branch, recursive=1)
    for file in content["tree"]:
        if "code_of_conduct.md" in file.path.lower():
            coc.extend([repo.url, file["path"]])
    return coc


def get_data_from_api(service: Service, repo: Repo, variable_type, verbose=True):
    """The function calls the ghapi api to retrieve

    Args:
        service (Service): Service object with API connection and metadata vars
        repo    (Repo)   : Repository variables bundled together
        variable_type (string): which type of variable should be retrieved. Supported are:
                                contributors, languages, jupyter_notebooks, readmes, coc
        verbose (boolean): if True, retrieve all variables from API.
            Otherwise, only collect username and contributions (only relevant for contributors)
    Returns:
        list: A list of the retrieved variables
    """
    retrieved_variables = []
    request_successful = False
    while not request_successful:
        try:
            if variable_type == "contributors":
                retrieved_variables.extend(
                    get_contributors(service, repo, verbose))
            elif variable_type == "languages":
                retrieved_variables.extend(get_languages(service, repo))
            elif variable_type == "jupyter_notebooks":
                retrieved_variables.extend(
                    get_jupyter_notebooks(service, repo))
            elif variable_type == "readmes":
                retrieved_variables.extend(
                    get_readmes(service, repo))
            elif variable_type == "coc":
                retrieved_variables.extend(
                    get_coc(service, repo))
        except Exception as e:  # pylint: disable=broad-except
            print(f"There was an error for repository {repo.url} : {e}")
            # (non-existing repo)
            if any(status_code in str(e) for status_code in ["204", "404"]):
                print(f"Repository does not exist: {repo.url}")
            elif "403" in str(e):  # timeout
                print("Github seems to have issues with users that are accessing API data from"
                      " an organization they are part of. It is not possible to distinguish"
                      " between this error and a timeout issue. In case this is an issue for"
                      " you, you can create a new Github account and generate a new token.")
                print("Sleep for a while.")
                for _ in range(100):
                    time.sleep(6)
                    continue
            else:
                print(
                    f"Unhandled status code: {e} - skip repository"
                )
            return None
        request_successful = True
        time.sleep(service.sleep)
        return retrieved_variables


if __name__ == '__main__':
    # if unauthorized API is used, rate limit is lower,
    # leading to a ban and waiting time needs to be increased
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    if token is None:
        SLEEP = 6
    else:
        SLEEP = 2
    serv = Service(api=GhApi(token=token), sleep=SLEEP)
    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument("--input",
                        "-i",
                        help="The file name of the repositories data.",
                        default="results/repositories_howfairis.csv")

    parser.add_argument("--contributors",
                        "-c",
                        action='store_true',
                        help="Set this flag if contributors should be retrieved")

    parser.add_argument("--contributors_output",
                        "-cout",
                        help="Optional. Path for contributors output",
                        default="results/contributors.csv")

    parser.add_argument(
        "--jupyter",
        "-j",
        action='store_true',
        help="Set this flag if jupyter notebooks should be retrieved")

    parser.add_argument(
        "--input_languages",
        "-ilang",
        help="Optional. Needed if languages are not retrieved but jupyter notebooks are."
    )

    parser.add_argument("--jupyter_output",
                        "-jout",
                        help="Optional. Path for jupyter notebooks output",
                        default="results/jupyter_notebooks.csv")

    parser.add_argument("--languages",
                        "-l",
                        action='store_true',
                        help="Set this flag if languages should be retrieved")

    parser.add_argument("--languages_output",
                        "-lout",
                        help="Optional. Path for languages output",
                        default="results/languages.csv")

    parser.add_argument("--topics",
                        "-t",
                        action='store_true',
                        help="Set this flag if topics should be retrieved")

    parser.add_argument("--topics_output",
                        "-tout",
                        help="Optional. Path for topics output",
                        default="results/topics.csv")

    parser.add_argument("--readmes",
                        "-r",
                        action='store_true',
                        help="Set this flag if readmes should be retrieved")

    parser.add_argument("--readmes_output",
                        "-rout",
                        help="Optional. Path for readmes output",
                        default="results/readmes.csv")

    parser.add_argument("--coc",
                        "-coc",
                        action='store_true',
                        help="Set this flag if code of conducts should be retrieved")

    parser.add_argument("--coc_output",
                        "-cocout",
                        help="Optional. Path for code of conduct output",
                        default="results/coc.csv")

    # Read arguments from the command line
    args = parser.parse_args()
    print(
        f"Retrieving howfairis variables for the following file: {args.input}")
    print(f"Retrieving contributors? {args.contributors}"
          f"\nRetrieving languages? {args.languages}"
          f"\nRetrieving jupyter notebooks? {args.jupyter}"
          f"\nRetrieving topics? {args.topics}"
          f"\nRetrieving readmes? {args.readmes}"
          f"\nRetrieving code of conducts? {args.coc}")

    df_repos = read_input_file(args.input)

    LANGUAGES = None

    if args.contributors:
        # get column names from arbitrary repo
        data = serv.api.repos.list_contributors("kequach", "HTML-Examples")
        if isinstance(data, L):
            column_headers = list(data[0].keys())
            all_column_headers = ["html_url_repository"] + column_headers
            time.sleep(serv.sleep)
        else:
            print("There was an error retrieving column names.")

        # get data
        contributors_variables = []
        for counter, (url, owner, repo_name) in enumerate(zip(df_repos["html_url"],
                                                              df_repos["owner"], df_repos["name"])):
            repository = Repo(url, owner, repo_name)
            retrieved_data = get_data_from_api(
                serv, repository, "contributors")
            if retrieved_data is not None:
                contributors_variables.extend(retrieved_data)
            if counter % 10 == 0:
                print(f"Parsed {counter} out of {len(df_repos.index)} repos.")

        export_file(contributors_variables, all_column_headers, "contributor",
                    args.contributors_output)

    if args.languages:
        # get languages
        language_variables = []
        for counter, (url, owner, repo_name) in enumerate(zip(df_repos["html_url"],
                                                              df_repos["owner"], df_repos["name"])):
            repository = Repo(url, owner, repo_name)
            retrieved_data = get_data_from_api(serv, repository, "languages")
            if retrieved_data is not None:
                language_variables.extend(retrieved_data)
            if counter % 10 == 0:
                print(f"Parsed {counter} out of {len(df_repos.index)} repos.")

        cols = ["html_url_repository", "language", "num_chars"]
        export_file(language_variables, cols,
                    "language", args.languages_output)
        if args.jupyter:  # keep df for parsing jupyter files
            LANGUAGES = pd.DataFrame(language_variables, columns=cols)

    if args.jupyter:
        if LANGUAGES is None:
            if args.input_languages is None:
                print(
                    "Please provide a file with languages that can be parsed for "
                    "jupyter notebooks.")
                sys.exit()
            else:
                LANGUAGES = read_input_file(args.input_languages)
        jupyter_variables = []
        languages_jupyter = LANGUAGES[LANGUAGES["language"] ==
                                      "Jupyter Notebook"].drop(
            ["language", "num_chars"], axis=1)
        print(f"Parse {len(languages_jupyter.index)} repos.")
        for counter, url in enumerate(languages_jupyter["html_url_repository"]):
            # example url: https://github.com/UtrechtUniversity/SWORDS-UU
            row = df_repos.loc[df_repos['html_url'] == url]
            branch = row["default_branch"].values[0]
            owner, repo_name = url.split("github.com/")[1].split("/")
            repository = Repo(url, owner, repo_name, branch)
            retrieved_data = get_data_from_api(
                serv, repository, "jupyter_notebooks")
            if retrieved_data is not None:
                jupyter_variables.extend(retrieved_data)
            if counter % 10 == 0:
                print(
                    f"Parsed {counter} out of {len(languages_jupyter.index)} repos.")
        export_file(jupyter_variables, ["html_url_repository", "path"], "jupyter notebook",
                    args.jupyter_output)

    if args.topics:
        topics_variables = []
        for (url, topics_str) in zip(df_repos["html_url"], df_repos["topics"]):
            topics = ast.literal_eval(topics_str)
            if len(topics) > 0:
                for topic in topics:
                    topic_entry = [url, topic]
                    topics_variables.append(topic_entry)

        export_file(topics_variables, ["html_url_repository", "topic"], "topic",
                    args.topics_output)

    if args.readmes:
        # get data
        readmes_variables = []
        for counter, (url, owner, repo_name) in enumerate(zip(df_repos["html_url"],
                                                              df_repos["owner"], df_repos["name"])):
            repository = Repo(url, owner, repo_name)
            retrieved_data = get_data_from_api(serv, repository, "readmes")
            print(retrieved_data)
            if retrieved_data is not None:
                readmes_variables.append(retrieved_data)
            if counter % 10 == 0:
                print(f"Parsed {counter} out of {len(df_repos.index)} repos.")

        export_file(readmes_variables, ["html_url_repository", "readme"], "readme",
                    args.readmes_output)

    if args.coc:
        # get data
        coc_variables = []
        for counter, (url, owner, repo_name,
                      branch) in enumerate(zip(df_repos["html_url"], df_repos["owner"],
                                               df_repos["name"], df_repos["default_branch"])):
            repository = Repo(url, owner, repo_name)
            retrieved_data = get_data_from_api(serv, repository, "coc")
            print(retrieved_data)
            if retrieved_data is not None:
                coc_variables.append(retrieved_data)
            if counter % 10 == 0:
                print(f"Parsed {counter} out of {len(df_repos.index)} repos.")

        export_file(coc_variables, ["html_url_repository", "coc"], "coc",
                    args.coc_output)
