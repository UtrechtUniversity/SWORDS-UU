"""
This file retrieves Github API variables for an input file with repositories.
"""
import os
import time
from datetime import datetime, timedelta
import ast
import argparse
import base64

import pandas as pd
from dotenv import load_dotenv
from ghapi.all import GhApi, paged
from fastcore.foundation import L


class Service:
    """
    Common variables used in functions bundled in Service class.
    """

    def __init__(self, api: GhApi, sleep=6):
        self.api = api
        self.current_date = datetime.today().strftime('%Y-%m-%d')
        self.sleep = sleep
        self.file_list = None


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


def get_file_locations(service: Service, repo: Repo, file_names):
    """Retrieves file locations of a file name search for a Github repository.

    Args:
        service    (Service): Service object with API connection and metadata vars
        repo       (Repo)   : Repository variables bundled together
        file_names (list)   : List of file names that should be searched.
                              Examples: ".ipynb", "CONTRIBUTING"

    Returns:
        list: file name list retrieved from Github
    """
    result = []
    content = service.api.git.get_tree(owner=repo.owner, repo=repo.repo_name,
                                       tree_sha=repo.branch, recursive=1)
    for file in content["tree"]:
        if any(file_name.lower() in file.path.lower() for file_name in file_names):
            file_names_entry = [repo.url, file["path"]]
            print(file_names_entry)
            result.append(file_names_entry)
    return result


def get_commit_variables(service: Service, repo: Repo):
    """Retrieves commit dates of a repository.
    Design decision to use slower sequential pagination to do less requests.
    Parallel pages retrieval required an additional request.

    Args:
        service (Service): Service object with API connection and metadata vars
        repo    (Repo)   : Repository variables bundled together

    Returns:
        list: list with url and three variables:
            correct version control usage (are there commits in the days after initial one?),
            life span of the repository measured as days between first and last commit,
            whether the repository is still active (was there a commit within the last 365 days?)
    """
    commit_pages = paged(service.api.repos.list_commits, owner=repo.owner,
                         repo=repo.repo_name, per_page=100)
    commit_dates = []
    result = []
    for page in commit_pages:
        for commit in page:
            commit_dates.append(datetime.strptime(commit["commit"]["author"]["date"],
                                                  "%Y-%m-%dT%H:%M:%SZ"))
            first_commit = commit # this will be the first commit after finishing the loops

    vcs_usage = commit_dates[0].date() != commit_dates[-1].date()
    life_span = (commit_dates[0].date() - commit_dates[-1].date()).days
    repo_active = (datetime.today().date() - commit_dates[0].date()) < timedelta(days=365)

    # no valid GitHub user did the first commit
    if first_commit["author"] is None or len(first_commit["author"]) == 0:
        first_commit_user = None
    else:
        first_commit_user = first_commit["author"]["login"]
    first_commit_date = commit_dates[-1].strftime('%Y-%m-%d')
    result.append([repo.url, vcs_usage, life_span,
                   repo_active, first_commit_user, first_commit_date])
    return result


def get_test_location(service: Service, repo: Repo):
    """Retrieves test folder locations for a Github repository.

    Args:
        service    (Service): Service object with API connection and metadata vars
        repo       (Repo)   : Repository variables bundled together

    Returns:
        list: test folder list retrieved from Github
    """
    result = []
    content = service.api.git.get_tree(owner=repo.owner, repo=repo.repo_name,
                                       tree_sha=repo.branch, recursive=1)
    for file in content["tree"]:
        if "test" in file.path.lower() and file.type == "tree":
            folder_names_entry = [repo.url, file["path"]]
            print(folder_names_entry)
            result.append(folder_names_entry)
            # if there is one positive result we can conclude that there are tests
            return result
    return result


def get_version_identifiability(service: Service, repo: Repo):
    """Retrieves identifiability with version scheme.
    All tags must follow the scheme: X.X or X.X.X
    If there are no tags, version compliance is false.
    No pagination used since tags are often empty, making it necessary to check
    for an empty generator, which is awkward and obfuscates the code.
    Tags have never exceeded n=100.

    Args:
        service (Service): Service object with API connection and metadata vars
        repo    (Repo)   : Repository variables bundled together

    Returns:
        list: repo url and compliance boolean
    """
    tags = service.api.repos.list_tags(owner=repo.owner,
                         repo=repo.repo_name, per_page=100)
    result = []
    version_identifiability = None
    if tags:
        for tag in tags:
            split = tag["name"].split(".")
            if len(split) in [2,3]:
                version_identifiability = True
            else: # all versions must follow the scheme. If one is wrong, exit
                version_identifiability = False
                break
        result.append([repo.url, version_identifiability])
        return result
    return result


def get_data_from_api(service: Service, repo: Repo, variable_type, verbose=True):
    """The function calls the ghapi api to retrieve

    Args:
        service (Service): Service object with API connection and metadata vars
        repo    (Repo)   : Repository variables bundled together
        variable_type (string): which type of variable should be retrieved. Supported are:
                                contributors, languages, readmes, files, commits, versions
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
            elif variable_type == "readmes":
                retrieved_variables.extend(
                    get_readmes(service, repo))
            elif variable_type == "files":
                retrieved_variables.extend(
                    get_file_locations(service, repo, service.file_list))
            elif variable_type == "tests":
                retrieved_variables.extend(
                    get_test_location(service, repo))
            elif variable_type == "commits":
                retrieved_variables.extend(
                    get_commit_variables(service, repo))
            elif variable_type == "versions":
                retrieved_variables.extend(
                    get_version_identifiability(service, repo))
        except Exception as e:  # pylint: disable=broad-except
            print(f"There was an error for repository {repo.url} : {e}")
            # (non-existing repo)
            if any(status_code in str(e) for status_code in ["204", "404"]):
                print(f"Repository does not exist: {repo.url}")
            elif "403" in str(e):  # timeout
                # this does not use time until token refresh as sleep time
                # due to the issue described in the print
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
            time.sleep(service.sleep)
            return None
        remaining_requests = service.api.rate_limit.get()["rate"]["remaining"]
        print(f"Remaining GitHub requests: {remaining_requests}")

        if remaining_requests < 5: # additional safety to not breach request limit
            sleep_time = service.api.rate_limit.get()["rate"]["reset"] - int(time.time())
            print(f"Reached request limit. Sleep for {sleep_time} seconds.")
            time.sleep(sleep_time)
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
        SLEEP = 0
    serv = Service(api=GhApi(token=token), sleep=SLEEP)
    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument("--input",
                        "-i",
                        help="The file name of the repositories data.",
                        default="../collect_repositories/results/repositories_filtered.csv")

    parser.add_argument("--contributors",
                        "-c",
                        action='store_true',
                        help="Set this flag if contributors should be retrieved")

    parser.add_argument("--contributors_output",
                        "-cout",
                        help="Optional. Path for contributors output",
                        default="results/contributors.csv")

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

    parser.add_argument("--files",
                        "-f",
                        type=str,
                        help="Delimited list of file (sub)strings that should be searched")

    parser.add_argument("--files_output",
                        "-fout",
                        help="Optional. Path for file location output",
                        default="results/files.csv")

    parser.add_argument("--tests",
                        "-tests",
                        action='store_true',
                        help="Set this flag if test folder paths should be retrieved")

    parser.add_argument("--tests_output",
                        "-tests_out",
                        help="Optional. Path for file location output",
                        default="results/test_paths.csv")

    parser.add_argument("--commits",
                        "-commits",
                        action='store_true',
                        help="Set this flag if commit-related variables should be retrieved")

    parser.add_argument("--commits_output",
                        "-commit_out",
                        help="Optional. Path for file location output",
                        default="results/commits.csv")

    parser.add_argument("--versions",
                        "-versions",
                        action='store_true',
                        help="Set this flag if version identifiability should be retrieved")

    parser.add_argument("--versions_output",
                        "-versions_out",
                        help="Optional. Path for version identifiability output",
                        default="results/versions.csv")

    # Read arguments from the command line
    args = parser.parse_args()
    print(
        f"Retrieving howfairis variables for the following file: {args.input}")
    print(f"Retrieving contributors? {args.contributors}"
          f"\nRetrieving languages? {args.languages}"
          f"\nRetrieving topics? {args.topics}"
          f"\nRetrieving readmes? {args.readmes}"
          f"\nRetrieving file locations for the following files: {args.files}"
          f"\nRetrieving test locations? {args.tests}"
          f"\nRetrieving commit variables? {args.commits}"
          f"\nRetrieving version variable? {args.versions}")

    df_repos = read_input_file(args.input)

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

    if args.files:
        # get data
        serv.file_list = args.files.split(",")
        file_variables = []
        for counter, (url, owner, repo_name,
                      branch) in enumerate(zip(df_repos["html_url"], df_repos["owner"],
                                               df_repos["name"], df_repos["default_branch"])):
            repository = Repo(url, owner, repo_name, branch)
            retrieved_data = get_data_from_api(serv, repository, "files")
            print(retrieved_data)
            if retrieved_data is not None:
                file_variables.extend(retrieved_data)
            if counter % 10 == 0:
                print(f"Parsed {counter} out of {len(df_repos.index)} repos.")

        export_file(file_variables, ["html_url_repository", "file_location"], "files",
                    args.files_output)


    if args.tests:
        # get data
        file_variables = []
        for counter, (url, owner, repo_name,
                      branch) in enumerate(zip(df_repos["html_url"], df_repos["owner"],
                                               df_repos["name"], df_repos["default_branch"])):
            repository = Repo(url, owner, repo_name, branch)
            retrieved_data = get_data_from_api(serv, repository, "tests")
            print(retrieved_data)
            if retrieved_data is not None:
                file_variables.extend(retrieved_data)
            if counter % 10 == 0:
                print(f"Parsed {counter} out of {len(df_repos.index)} repos.")

        export_file(file_variables, ["html_url_repository", "file_location"], "tests",
                    args.tests_output)


    if args.commits:
        # get data
        commit_variables = []
        for counter, (url, owner, repo_name) in enumerate(zip(df_repos["html_url"],
                                                              df_repos["owner"], df_repos["name"])):
            repository = Repo(url, owner, repo_name)
            retrieved_data = get_data_from_api(serv, repository, "commits")
            print(retrieved_data)
            if retrieved_data is not None:
                commit_variables.extend(retrieved_data)
            if counter % 10 == 0:
                print(f"Parsed {counter} out of {len(df_repos.index)} repos.")

        export_file(commit_variables, ["html_url_repository", "vcs_usage", "life_span",
                    "first_commit_user", "first_commit_date", "repo_active"],
                    "commits", args.commits_output)


    if args.versions:
        # get data
        version_variables = []
        for counter, (url, owner, repo_name) in enumerate(zip(df_repos["html_url"],
                                                              df_repos["owner"], df_repos["name"])):
            repository = Repo(url, owner, repo_name)
            retrieved_data = get_data_from_api(serv, repository, "versions")
            print(retrieved_data)
            if retrieved_data is not None:
                version_variables.extend(retrieved_data)
            if counter % 10 == 0:
                print(f"Parsed {counter} out of {len(df_repos.index)} repos.")

        export_file(version_variables, ["html_url_repository", "version_identifiable"],
                    "version identifiability", args.versions_output)
