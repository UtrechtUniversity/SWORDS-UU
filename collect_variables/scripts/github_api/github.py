"""
This file retrieves Github API variables for an input file with repositories.
"""
import os
import sys
import time
from datetime import datetime
import ast
import argparse

import pandas as pd
from dotenv import load_dotenv
from ghapi.all import GhApi
from fastcore.foundation import L
from fastcore.net import ExceptionsHTTP


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


def get_contributors(contributors_url, contributors_owner, contributors_repo_name, verbose):
    """Retrieves contributors for a Github repository

    Args:
        contributors_url (string): repository url
        contributors_owner (string): repository owner
        contributors_repo_name (string): repository name

    Returns:
        list: contributors list retrieved from Github
    """
    contributors = []
    contributors_data = api.repos.list_contributors(
        owner=contributors_owner, repo=contributors_repo_name, anon=1, per_page=100)
    for contributor in contributors_data:
        entry = [contributors_url]
        entry.extend(list(contributor.values()))
        print(entry[0:2])
        contributors.append(entry)
    return contributors


def get_languages(languages_url, languages_owner, languages_repo_name):
    """Retrieves languages for a Github repository

    Args:
        languages_url (string): repository url
        languages_owner (string): repository owner
        languages_repo_name (string): repository name

    Returns:
        list: languages list retrieved from Github
    """
    languages = []
    languages_data = api.repos.list_languages(
        owner=languages_owner, repo=languages_repo_name)
    for language, num_chars in languages_data.items():
        languages_entry = [languages_url]
        languages_entry.extend([language, num_chars])
        print(languages_entry)
        languages.append(languages_entry)
    return languages


def get_jupyter_notebooks(jupyter_notebooks_url,
                          jupyter_notebooks_owner, jupyter_notebooks_repo_name):
    """Retrieves jupyter notebooks for a Github repository

    Args:
        jupyter_notebooks_url (string): repository url
        jupyter_notebooks_owner (string): repository owner
        jupyter_notebooks_repo_name (string): repository name

    Returns:
        list: jupyter notebooks file name list retrieved from Github
    """
    jupyter_notebooks = []
    jupyter_notebooks_data = api.git.get_tree(
        owner=jupyter_notebooks_owner, repo=jupyter_notebooks_repo_name,
        tree_sha="master", recursive=1)
    for file in jupyter_notebooks_data["tree"]:
        if file["type"] == "blob" and ".ipynb" in file["path"]:
            jupyter_notebooks_entry = [jupyter_notebooks_url, file["path"]]
            print(jupyter_notebooks_entry)
            jupyter_notebooks.append(jupyter_notebooks_entry)
    return jupyter_notebooks


def get_data_from_api(github_url, github_owner, github_repo_name, variable_type):
    """The function calls the ghapi api to retrieve

    Args:
        github_url (string): repository url.
                      E.g.: https://api.github.com/repos/kequach/HTML-Examples/contributors
        github_owner (string): repository owner. E.g.: kequach
        github_repo_name (string): repository name. E.g.: HTML-Examples
        variable_type (string): which type of variable should be retrieved.
                                Supported are: contributors, languages, jupyter_notebooks
    Returns:
        list: A list of the retrieved variables
    """
    retrieved_variables = []
    request_successful = False
    while not request_successful:
        try:
            if variable_type == "contributors":
                retrieved_variables.extend(
                    get_contributors(github_url, github_owner, github_repo_name))
            elif variable_type == "languages":
                retrieved_variables.extend(
                    get_languages(github_url, github_owner, github_repo_name))
            elif variable_type == "jupyter_notebooks":
                retrieved_variables.extend(
                    get_jupyter_notebooks(github_url, github_owner, github_repo_name))
        except ExceptionsHTTP as e:
            print(f"There was an error: {e}")
            # (non-existing repo)
            if any(status_code in e for status_code in ["204", "404"]):
                print(f"Repository does not exist: {github_url}")
            elif "403" in e:  # timeout
                print("Sleep for a while.")
                for _ in range(100):
                    time.sleep(6)
                    continue
            else:
                print(
                    f"Unhandled status code: {e} - skip repository"
                )
        request_successful = True
        return retrieved_variables


# if unauthorized API is used, rate limit is lower,
# leading to a ban and waiting time needs to be increased
load_dotenv()
token = os.getenv('GITHUB_TOKEN')
api = GhApi(token=token)
if token is None:
    SLEEP = 6
else:
    SLEEP = 2

if __name__ == '__main__':
    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument("--input",
                        "-i",
                        help="The file name of the repositories data.",
                        default="output/repositories_howfairis.csv")

    parser.add_argument("--contributors",
                        "-c",
                        action='store_true',
                        help="Set this flag if contributors should be retrieved")

    parser.add_argument("--contributors_output",
                        "-cout",
                        help="Optional. Path for contributors output",
                        default="output/contributors.csv")

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
                        default="output/jupyter_notebooks.csv")

    parser.add_argument("--languages",
                        "-l",
                        action='store_true',
                        help="Set this flag if languages should be retrieved")

    parser.add_argument("--languages_output",
                        "-lout",
                        help="Optional. Path for languages output",
                        default="output/languages.csv")

    parser.add_argument("--topics",
                        "-t",
                        action='store_true',
                        help="Set this flag if topics should be retrieved")

    parser.add_argument("--topics_output",
                        "-tout",
                        help="Optional. Path for topics output",
                        default="output/topics.csv")

    # Read arguments from the command line
    args = parser.parse_args()
    print(
        f"Retrieving howfairis variables for the following file: {args.input}")
    print(f"Retrieving contributors? {args.contributors}"
          f"\nRetrieving jupyter notebooks? {args.jupyter}"
          f"\nRetrieving languages? {args.languages}"
          f"\nRetrieving topics? {args.topics}")

    df_repos = read_input_file(args.input)
    df_repos = df_repos.head(10)

    LANGUAGES = None

    if args.contributors:
        # get column names from arbitrary repo
        data = api.repos.list_contributors("kequach", "HTML-Examples")
        if isinstance(data, L):
            column_headers = list(data[0].keys())
            all_column_headers = ["html_url_repository"] + column_headers
            time.sleep(SLEEP)
        else:
            print("There was an error retrieving column names.")

        # get data
        contributors_variables = []
        for counter, (url, owner, repo_name) in enumerate(zip(df_repos["html_url"],
                                                              df_repos["owner"], df_repos["name"])):
            contributors_variables.extend(get_data_from_api(
                url, owner, repo_name, "contributors"))
            if counter % 10 == 0:
                print(f"Parsed {counter} out of {len(df_repos.index)} repos.")
            time.sleep(SLEEP)

        export_file(contributors_variables, all_column_headers, "contributor",
                    args.contributors_output)

    if args.languages:
        # get languages
        language_variables = []
        for counter, (url, owner, repo_name) in enumerate(zip(df_repos["html_url"],
                                                              df_repos["owner"], df_repos["name"])):
            language_variables.extend(get_data_from_api(
                url, owner, repo_name, "languages"))

            if counter % 10 == 0:
                print(f"Parsed {counter} out of {len(df_repos.index)} repos.")
            time.sleep(SLEEP)

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
        for counter, repo_url in enumerate(languages_jupyter["html_url_repository"]):
            # example repo_url: https://github.com/UtrechtUniversity/SWORDS-UU
            owner, repo_name = repo_url.split("github.com/")[1].split("/")
            jupyter_variables.extend(get_data_from_api(
                url, owner, repo_name, "languages"))
            if counter % 10 == 0:
                print(
                    f"Parsed {counter} out of {len(languages_jupyter.index)} repos.")
            time.sleep(SLEEP)
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
