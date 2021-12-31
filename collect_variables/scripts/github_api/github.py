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


def get_data_from_api(url, owner, repo_name, variable_type):
    """The function calls the ghapi api to retrieve

    Args:
        url (string): repository url. E.g.: https://api.github.com/repos/kequach/HTML-Examples/contributors
        owner (string): repository owner. E.g.: kequach
        repo_name (string): repository name. E.g.: HTML-Examples
        variable_type (string): which type of variable should be retrieved. Supported are: contributors, languages, jupyter_notebooks
    Returns:
        list: A list of the retrieved variables
    """
    retrieved_variables = []
    request_successful = False
    while not request_successful:
        try:
            if variable_type == "contributors":
                data = api.repos.list_contributors(
                    owner=owner, repo=repo_name, anon=1, per_page=100)
                for contributor in data:
                    entry = [url]
                    entry.extend(list(contributor.values()))
                    print(entry[0:2])
                    retrieved_variables.append(entry)
            elif variable_type == "languages":
                data = api.repos.list_languages(owner=owner, repo=repo_name)
                for language, num_chars in data.items():
                    entry = [url]
                    entry.extend([language, num_chars])
                    print(entry)
                    retrieved_variables.append(entry)
            elif variable_type == "jupyter_notebooks":
                data = api.git.get_tree(
                    owner=owner, repo=repo_name, tree_sha="master", recursive=1)
                for file in data["tree"]:
                    if file["type"] == "blob" and ".ipynb" in file["path"]:
                        entry = [repo_url, file["path"]]
                        print(entry)
                        variables.append(entry)
        except ExceptionsHTTP as e:
            print(f"There was an error: {e}")
            # (non-existing repo)
            if any(status_code in e for status_code in ["204", "404"]):
                print(f"Repository does not exist: {url}")
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
print(f"Retrieving howfairis variables for the following file: {args.input}")
print(f"Retrieving contributors? {args.contributors}"
      f"\nRetrieving jupyter notebooks? {args.jupyter}"
      f"\nRetrieving languages? {args.languages}"
      f"\nRetrieving topics? {args.topics}")

# if unauthorized API is used, rate limit is lower,
# leading to a ban and waiting time needs to be increased
load_dotenv()
token = os.getenv('GITHUB_TOKEN')
api = GhApi(token=token)

headers = {'Authorization': 'token ' + token}
params = {
    'per_page': 100,
}

df_repos = read_input_file(args.input)
df_repos = df_repos.head(10)
if token is None:
    SLEEP = 6
else:
    SLEEP = 2

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
    variables = []
    for COUNTER, (url, owner, repo_name) in enumerate(zip(df_repos["html_url"], df_repos["owner"], df_repos["name"])):
        variables.extend(get_data_from_api(
            url, owner, repo_name, "contributors"))
        if COUNTER % 10 == 0:
            print(f"Parsed {COUNTER} out of {len(df_repos.index)} repos.")
        time.sleep(SLEEP)

    export_file(variables, all_column_headers, "contributor",
                args.contributors_output)

if args.languages:
    # get languages
    variables = []
    for COUNTER, (url, owner, repo_name) in enumerate(zip(df_repos["html_url"], df_repos["owner"], df_repos["name"])):
        variables.extend(get_data_from_api(
            url, owner, repo_name, "languages"))

        if COUNTER % 10 == 0:
            print(f"Parsed {COUNTER} out of {len(df_repos.index)} repos.")
        time.sleep(SLEEP)

    cols = ["html_url_repository", "language", "num_chars"]
    export_file(variables, cols, "language", args.languages_output)
    if args.jupyter:  # keep df for parsing jupyter files
        LANGUAGES = pd.DataFrame(variables, columns=cols)

if args.jupyter:
    if LANGUAGES is None:
        if args.input_languages is None:
            print(
                "Please provide a file with languages that can be parsed for jupyter notebooks.")
            sys.exit()
        else:
            LANGUAGES = read_input_file(args.input_languages)
    variables = []
    languages_jupyter = LANGUAGES[LANGUAGES["language"] ==
                                  "Jupyter Notebook"].drop(
                                      ["language", "num_chars"], axis=1)
    print(f"Parse {len(languages_jupyter.index)} repos.")
    for COUNTER, repo_url in enumerate(languages_jupyter["html_url_repository"]):
        # example repo_url: https://github.com/UtrechtUniversity/SWORDS-UU
        owner, repo_name = repo_url.split("github.com/")[1].split("/")
        variables.extend(get_data_from_api(url, owner, repo_name, "languages"))
        if COUNTER % 10 == 0:
            print(
                f"Parsed {COUNTER} out of {len(languages_jupyter.index)} repos.")
        time.sleep(SLEEP)
    export_file(variables, ["html_url_repository", "path"], "jupyter notebook",
                args.jupyter_output)

if args.topics:
    variables = []
    for (url, topics_str) in zip(df_repos["html_url"], df_repos["topics"]):
        topics = ast.literal_eval(topics_str)
        if len(topics) > 0:
            for topic in topics:
                entry = [url, topic]
                variables.append(entry)

    export_file(variables, ["html_url_repository", "topic"], "topic",
                args.topics_output)
