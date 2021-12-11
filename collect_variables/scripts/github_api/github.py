"""
This file retrieves Github API variables for an input file with repositories.
"""
import os
import time
from datetime import datetime
import ast
import argparse

import pandas as pd
from dotenv import load_dotenv
import requests


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
    help=
    "Optional. Needed if languages are not retrieved but jupyter notebooks are."
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
headers = {'Authorization': 'token ' + token}
params = {
    'per_page': 100,
}

df_repos = read_input_file(args.input)
if token is None:
    SLEEP = 6
else:
    SLEEP = 2

LANGUAGES = None

if args.contributors:

    # get column names from arbitrary repo
    URL = "https://api.github.com/repos/kequach/HTML-Examples/contributors"
    r = requests.get(url=URL, headers=headers)
    data = r.json()
    if isinstance(data, list):
        column_headers = list(data[0].keys())
        all_column_headers = ["html_url_repository"] + column_headers
        time.sleep(SLEEP)
    else:
        print("There was an error retrieving column names.")

    # get data
    variables = []
    for COUNTER, (url, contributor_url) in enumerate(
            zip(df_repos["html_url"], df_repos["contributors_url"])):
        REQUEST_SUCCESSFUL = False
        while not REQUEST_SUCCESSFUL:
            r = requests.get(url=contributor_url,
                             headers=headers,
                             params=params)
            print(r, contributor_url)
            if r.status_code == 200:
                data = r.json()
                for contributor in data:
                    entry = [url]
                    entry.extend(list(contributor.values()))
                    print(entry[0:2])
                    variables.append(entry)
            elif r.status_code == 403:  # timeout
                print(f"There was a problem: {contributor_url}")
                print("Sleep for a while.")
                for i in range(100):
                    time.sleep(6)
                    continue
            elif r.status_code in [204, 404]:  # (non-existing repo)
                print(f"Repository does not exist: {url}")
            else:
                print(f"Unhandled status code: {r.status_code} - skip repository")

            REQUEST_SUCCESSFUL = True
            time.sleep(SLEEP)

            if COUNTER % 10 == 0:
                print("Parsed %d out of %d repos." %
                      (COUNTER, len(df_repos.index)))

    export_file(variables, all_column_headers, "contributor",
                args.contributors_output)

if args.languages:
    # get languages
    variables = []
    for COUNTER, (url, languages_url) in enumerate(
            zip(df_repos["html_url"], df_repos["languages_url"])):
        REQUEST_SUCCESSFUL = False
        while not REQUEST_SUCCESSFUL:
            r = requests.get(url=languages_url, headers=headers)
            print(r, url, languages_url)
            if r.status_code == 200:
                data = r.json()
                for language, num_chars in data.items():
                    entry = [url]
                    entry.extend([language, num_chars])
                    print(entry)
                    variables.append(entry)
            elif r.status_code == 403:  # timeout
                print("There was a problem: %s" % languages_url)
                print("Sleep for a while.")
                for i in range(100):
                    time.sleep(6)
                    continue
            elif r.status_code in [204, 404]:  # (non-existing repo)
                print("Repository does not exist: %s" % url)
            else:
                print("Unhandled status code: %d - skip repository" %
                      r.status_code)

            REQUEST_SUCCESSFUL = True
            time.sleep(SLEEP)
            if COUNTER % 10 == 0:
                print("Parsed %d out of %d repos." %
                      (COUNTER, len(df_repos.index)))

    cols = ["html_url_repository", "language", "num_chars"]
    export_file(variables, cols, "language", args.languages_output)
    if args.jupyter:  # keep df for parsing jupyter files
        LANGUAGES = pd.DataFrame(variables, columns=cols)

if args.jupyter:
    if LANGUAGES is None:
        if args.input_languages is None:
            print(
                "Please provide a file with languages that can be parsed for jupyter notebooks."
            )
            quit()
        else:
            LANGUAGES = read_input_file(args.input_languages)
    variables = []
    COUNTER = 0
    languages_jupyter = LANGUAGES[LANGUAGES["language"] ==
                                  "Jupyter Notebook"].drop(
                                      ["language", "num_chars"], axis=1)
    print("Parse %d repos." % len(languages_jupyter["html_url_repository"]))
    for repo_url in languages_jupyter["html_url_repository"]:
        repo_string = repo_url.split("github.com/")[1]
        # see: https://stackoverflow.com/a/61656698/5708610
        api_string = "https://api.github.com/repos/" + repo_string + "/git/trees/master?recursive=1"
        REQUEST_SUCCESSFUL = False
        while not REQUEST_SUCCESSFUL:
            r = requests.get(url=api_string, headers=headers)
            print(r, repo_url)
            if r.status_code == 200:
                data = r.json()
                for file in data["tree"]:
                    if file["type"] == "blob" and ".ipynb" in file["path"]:
                        entry = [repo_url, file["path"]]
                        print(entry)
                        variables.append(entry)
            elif r.status_code == 403:  # timeout
                print("There was a problem.")
                print("Sleep for a while.")
                for i in range(100):
                    time.sleep(6)
                    continue
            elif r.status_code in [204, 404]:  # (non-existing repo)
                print("Repository does not exist: %s" % repo_url)
            else:
                print("Unhandled status code: %d - skip repository" %
                      r.status_code)

            REQUEST_SUCCESSFUL = True
            COUNTER += 1
            time.sleep(SLEEP)
            if COUNTER % 10 == 0:
                print("Parsed %d out of %d repos." %
                      (COUNTER, len(languages_jupyter.index)))

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
