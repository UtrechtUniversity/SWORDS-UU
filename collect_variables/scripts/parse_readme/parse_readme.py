"""
This file parses an input readme file for related FAIR variables.
"""
import re
from datetime import datetime
import argparse

import pandas as pd


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


if __name__ == '__main__':
    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument("--input",
                        "-i",
                        help="The file name of the readme data",
                        default="../results/readmes.csv")

    parser.add_argument("--output",
                        "-out",
                        help="Optional. Path for the output",
                        default="results/readme_variables.csv")

    # Read arguments from the command line
    args = parser.parse_args()
    print(
        f"Retrieving readme variables for the following file: {args.input}")


    df_repos = read_input_file(args.input)
    df_repos = df_repos.dropna()
    results = []
    for url, readme in zip(df_repos["html_url_repository"], df_repos["readme"]):
        install_instruction = bool(re.search("install|docker", readme))
        usage_example = bool(re.search("usage|getting started|quick start|example|tutorial",
                                       readme))
        contrib_guidelines = bool(re.search("contribut", readme))
        results.append([url, install_instruction, usage_example, contrib_guidelines])
    print(results)

    df_results = pd.DataFrame(results,
                                columns=[
                                    "html_url", "has_install_instruction",
                                    "has_usage_examples", "has_contrib_guidelines"
                                ])

    print(df_results["has_install_instruction"].value_counts())
    print(df_results["has_usage_examples"].value_counts())
    print(df_results["has_contrib_guidelines"].value_counts())

    current_date = datetime.today().strftime('%Y-%m-%d')
    df_results["date"] = current_date
    df_results.to_csv(args.output, index=False)

    print(
        f"Successfully retrieved readme variables. Saved result to {args.output}."
    )
