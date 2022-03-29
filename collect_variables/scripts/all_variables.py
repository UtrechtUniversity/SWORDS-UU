"""
This file retrieves all variables in JSON format. Used for Kibana dashboard visualization.
"""
import time
import os
import ast
import argparse
import simplejson as json
from dotenv import load_dotenv
from ghapi.all import GhApi

from github_api.github import get_data_from_api, read_input_file, Service, Repo
from howfairis_api.howfairis_variables import parse_repo


def add_data_from_api(service, repo, variable_type, keys):
    """Retrieves Github API data. Utilizes the function from github_api/github.py to do so.
    This function adds the retrieved variables directly to the data dictionary.

    Args:
        service (Service): Service object with API connection and metadata vars
        repo    (Repo)   : Repository variables bundled together
        variable_type (string): which type of variable should be retrieved.
                                Supported are: contributors, languages, readmes
        keys (list): A list of the keys for the retrieved data
    Returns:
        boolean: Whether the request was successful or not.
        In case of unsuccessful request, skip repository
    """
    # for nested data only, otherwise key can be directly used
    if variable_type in ("contributors", "languages"):
        data[variable_type] = []
    retrieved_data = get_data_from_api(service, repo, variable_type, verbose=False)
    if retrieved_data is not None:
        if variable_type in ("contributors", "languages"):
            for entry in retrieved_data:
                data[variable_type].append(dict(zip(keys, entry[1:])))
        elif variable_type == "readmes":
            data[keys[0]] = retrieved_data[1]
    else:
        return False
    time.sleep(2)
    return True


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    serv = Service(api=GhApi(token=token))
    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument("--input",
                        "-i",
                        help="The file name of the repositories data.",
                        default="../collect_repositories/results/repositories_filtered.csv")

    parser.add_argument("--output",
                        "-o",
                        help="The file name of the output.",
                        default="results/all_variables.json")

    # Read arguments from the command line
    args = parser.parse_args()
    df_repos = read_input_file(args.input)




    for counter, row in df_repos.iterrows():
        url, owner = row["html_url"], row["owner"]
        repo_name, description = row["name"], row["description"]
        branch = row["default_branch"]
        topics_str = row["topics"]
        general_keys = ["url", "owner", "repository_name",
                        "date_all_variable_collection", "description"]
        general_values = [url, owner, repo_name, serv.current_date, description]
        data = dict(zip(general_keys, general_values))

        # remove topics from index slice to not have topics twice
        row.drop(labels="topics", inplace=True)
        # add all Github data after the API links
        data.update(row[54:78].items())

        contrib_keys = ["contributor", "contributions"]
        lang_keys = ["language", "num_chars"]
        howfairis_keys = ["howfairis_repository", "howfairis_license", "howfairis_registry",
                          "howfairis_citation", "howfairis_checklist"]
        readme_key = ["readme"]

        repository = Repo(repo_url = url,
                          repo_owner = owner,
                          repo_repo_name=repo_name,
                          repo_branch=branch)

        REQUEST_SUCCESSFUL = add_data_from_api(serv, repository, "contributors", contrib_keys)
        if REQUEST_SUCCESSFUL:
            howfairis_values = parse_repo(url)
            data["howfairis"] = dict(zip(howfairis_keys, howfairis_values[1:]))
            topics = ast.literal_eval(topics_str)
            data["topics"] = topics
            add_data_from_api(serv, repository, "languages", lang_keys)
            add_data_from_api(serv, repository, "readmes", readme_key)
            print(data)

            with open(args.output, "a", encoding="utf8") as fp:
                json.dump(data, fp, ignore_nan=True)
                fp.write("\n")
        else:
            print(
                f"Repository {repo_name} encountered issues, most likely repository does not"
                 "exist anymore or is private. Skipping repository."
            )
        if counter % 10 == 0:
            print(f"Parsed {counter} out of {len(df_repos.index)} repos.")
