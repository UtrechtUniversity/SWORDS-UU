import os
import time
from pathlib import Path
from datetime import datetime
import ast
import argparse

import pandas as pd
from dotenv import load_dotenv
import requests


def read_pandas_file(file_path):
    if ("xlsx" in file_path):
        return pd.read_excel(file_path, engine='openpyxl')
    else:
        return pd.read_csv(file_path)


def export_file(variables, columns, var_type, output):
    df_data = pd.DataFrame(variables, columns=columns)
    current_date = datetime.today().strftime('%Y-%m-%d')
    output_path = output + "_" + current_date + ".csv"
    df_data.to_csv(Path(output_path), index=False)
    print(
        f"Successfully retrieved {var_type} variables. Saved result to {output_path}."
    )


# Initiate the parser
parser = argparse.ArgumentParser()

# Add arguments to be parsed
parser.add_argument("--input",
                    "-i",
                    help="The file name of the repositories data.",
                    required=True)

parser.add_argument("--contributors",
                    "-c",
                    action='store_true',
                    help="Set this flag if contributors should be retrieved")

parser.add_argument("--contributors_output",
                    "-cout",
                    help="Optional. Path for contributors output",
                    default="output/contributors")

parser.add_argument(
    "--jupyter",
    "-j",
    action='store_true',
    help="Set this flag if jupyter notebooks should be retrieved")

parser.add_argument(
    "--input_languages",
    "-ilang",
    help=
    "Optional. If languages are not retrieved but jupyter notebooks should be, there needs to be an input file."
)

parser.add_argument("--jupyter_output",
                    "-jout",
                    help="Optional. Path for jupyter notebooks output",
                    default="output/jupyter_notebooks")

parser.add_argument("--languages",
                    "-l",
                    action='store_true',
                    help="Set this flag if languages should be retrieved")

parser.add_argument("--languages_output",
                    "-lout",
                    help="Optional. Path for languages output",
                    default="output/languages")

parser.add_argument("--topics",
                    "-t",
                    action='store_true',
                    help="Set this flag if topics should be retrieved")

parser.add_argument("--topics_output",
                    "-tout",
                    help="Optional. Path for topics output",
                    default="output/topics")

# Read arguments from the command line
args = parser.parse_args()
print(f"Retrieving howfairis variables for the following file: {args.input}")
print(
    f"Retrieving contributors? {args.contributors} \nRetrieving jupyter notebooks? {args.jupyter} \nRetrieving languages? {args.languages}\nRetrieving topics? {args.topics}"
)

# if unauthorized API is used, rate limit is lower leading to a ban and waiting time needs to be increased
load_dotenv()
token = os.getenv('GITHUB_TOKEN')
headers = {'Authorization': 'token ' + token}
params = {
    'per_page': 100,
}

df_repos = read_pandas_file(args.input)
if (token is None):
    sleep = 6
else:
    sleep = 2

languages = None

if (args.contributors):

    # get column names
    url = "https://api.github.com/repos/kequach/HTML-Examples/contributors"  # arbitrary repo to retrieve column names
    r = requests.get(url=url, headers=headers)
    data = r.json()
    if isinstance(data, list):
        column_headers = list(data[0].keys())
        all_column_headers = ["html_url_repository"] + column_headers
        time.sleep(sleep)
    else:
        print("There was an error retrieving column names.")

    # get data
    variables = []
    for counter, (url, contributor_url) in enumerate(
            zip(df_repos["html_url"], df_repos["contributors_url"])):
        request_successful = False
        while (not request_successful):
            r = requests.get(url=contributor_url,
                             headers=headers,
                             params=params)
            print(r, contributor_url)
            if (r.status_code == 200):
                data = r.json()
                for contributor in data:
                    entry = [url]
                    entry.extend(list(contributor.values()))
                    print(entry[0:2])
                    variables.append(entry)
            elif (r.status_code == 403):  # timeout
                print("There was a problem: %s" % contributor_url)
                print("Sleep for a while.")
                for i in range(100):
                    time.sleep(6)
                    continue
            elif (r.status_code in [204, 404]):  # (non-existing repo)
                print("Repository does not exist: %s" % url)
            else:
                print("Unhandled status code: %d - skip repository" %
                      r.status_code)

            request_successful = True
            time.sleep(sleep)

            if (counter % 10 == 0):
                print("Parsed %d out of %d repos." %
                      (counter, len(df_repos.index)))

    export_file(variables, all_column_headers, "contributor",
                args.contributors_output)

if (args.languages):
    # get languages
    variables = []
    for counter, (url, languages_url) in enumerate(
            zip(df_repos["html_url"], df_repos["languages_url"])):
        request_successful = False
        while (not request_successful):
            r = requests.get(url=languages_url, headers=headers)
            print(r, url, languages_url)
            if (r.status_code == 200):
                data = r.json()
                for language, num_chars in data.items():
                    entry = [url]
                    entry.extend([language, num_chars])
                    print(entry)
                    variables.append(entry)
            elif (r.status_code == 403):  # timeout
                print("There was a problem: %s" % languages_url)
                print("Sleep for a while.")
                for i in range(100):
                    time.sleep(6)
                    continue
            elif (r.status_code in [204, 404]):  # (non-existing repo)
                print("Repository does not exist: %s" % url)
            else:
                print("Unhandled status code: %d - skip repository" %
                      r.status_code)

            request_successful = True
            time.sleep(sleep)
            if (counter % 10 == 0):
                print("Parsed %d out of %d repos." %
                      (counter, len(df_repos.index)))

    cols = ["html_url_repository", "language", "num_chars"]
    export_file(variables, cols, "language", args.languages_output)
    if (args.jupyter):  # keep df for parsing jupyter files
        languages = pd.DataFrame(variables, columns=cols)

if (args.jupyter):
    if (languages is None):
        if (args.input_languages is None):
            print(
                "Please provide a file with languages that can be parsed for jupyter notebooks."
            )
            quit()
        else:
            languages = read_pandas_file(args.input_languages)
    variables = []
    counter = 0
    languages_jupyter = languages[languages["language"] ==
                                  "Jupyter Notebook"].drop(
                                      ["language", "num_chars"], axis=1)
    print("Parse %d repos." % len(languages_jupyter["html_url_repository"]))
    for repo_url in languages_jupyter["html_url_repository"]:
        repo_string = repo_url.split("github.com/")[1]
        api_string = "https://api.github.com/repos/" + repo_string + "/git/trees/master?recursive=1"  # see: https://stackoverflow.com/a/61656698/5708610
        request_successful = False
        while (not request_successful):
            r = requests.get(url=api_string, headers=headers)
            print(r, repo_url)
            if (r.status_code == 200):
                data = r.json()
                for file in data["tree"]:
                    if (file["type"] == "blob" and ".ipynb" in file["path"]):
                        entry = [repo_url, file["path"]]
                        print(entry)
                        variables.append(entry)
            elif (r.status_code == 403):  # timeout
                print("There was a problem: %s" % contributor_url)
                print("Sleep for a while.")
                for i in range(100):
                    time.sleep(6)
                    continue
            elif (r.status_code in [204, 404]):  # (non-existing repo)
                print("Repository does not exist: %s" % repo_url)
            else:
                print("Unhandled status code: %d - skip repository" %
                      r.status_code)

            request_successful = True
            counter += 1
            time.sleep(sleep)
            if (counter % 10 == 0):
                print("Parsed %d out of %d repos." %
                      (counter, len(languages_jupyter.index)))

    export_file(variables, ["html_url_repository", "path"], "jupyter notebook",
                args.jupyter_output)

if (args.topics):
    variables = []
    for (url, topics_str) in zip(df_repos["html_url"], df_repos["topics"]):
        topics = ast.literal_eval(topics_str)
        if (len(topics) > 0):
            for topic in topics:
                entry = [url, topic]
                variables.append(entry)

    export_file(variables, ["html_url_repository", "topic"], "topic",
                args.topics_output)
