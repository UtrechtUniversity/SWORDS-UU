"""
This file retrieves Github usernames from PURE research output
"""
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd
import rispy


def get_username_from_text(text):
    """Parses the PURE text for usernames

    Args:
        text (string): Text to be parsed

    Returns:
        string: Username
    """
    retrieved_user = None
    for word in text:
        if "github.com" in word:
            split = word.split("github.com/")
            retrieved_user = split[1].split("/")[0]
        elif "github.io" in word:
            githubio_split = word.split(".")
            retrieved_user = githubio_split[0].split("://")[1]
    return retrieved_user


if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Input file")
    args = parser.parse_args()

    users = []
    SERVICE = "github.com"
    current_date = datetime.today().strftime('%Y-%m-%d')

    with open(args.file, 'r', encoding="utf8") as pure_data:
        entries = rispy.load(pure_data)
        for entry in entries:
            user = get_username_from_text(entry.values())
            if user is not None:
                users.append([SERVICE, current_date, user])

        print(f"Successfully parsed file {args.file}.")
        pd.DataFrame(users,
                     columns=["service", "date",
                              "user_id"]).to_csv(Path("results", "pure.csv"),
                                                 index=False)
