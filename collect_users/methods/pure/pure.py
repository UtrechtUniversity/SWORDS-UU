import argparse
from pathlib import Path

import pandas as pd
import rispy


def get_username_from_text(text):
    for word in text:
        if "github.com" in word:
            split = word.split("github.com/")
            user = split[1].split("/")[0]
            return user
        elif "github.io" in word:
            githubio_split = word.split(".")
            user = githubio_split[0].split("://")[1]
            return user
    return None


if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Input file")
    args = parser.parse_args()

    users = list()
    service = "github.com"
    with open(args.file, 'r', encoding="utf8") as pure_data:
        entries = rispy.load(pure_data)
        for entry in entries:
            user = get_username_from_text(entry.values())
            if (user is not None):
                users.append([service, user])

        print(f"Successfully parsed file {args.file}.")
        pd.DataFrame(users,
                     columns=["service",
                              "user_id"]).to_csv(Path("results",
                                                      "ids_pure_users.csv"),
                                                 index=False)
