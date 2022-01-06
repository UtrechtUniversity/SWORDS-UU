"""
This file retrieves Github usernames from PapersWithCode.com
"""
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_username_from_string(url_github):
    """Parses a Github url for the username

    Args:
        url (string): Github.com url

    Returns:
        string: username
    """
    user = None
    if "github.com" in url_github:
        split = url_github.split("github.com/")
        # get value after "github.com/" and split after the next slash,
        # then the first value of that split will be the username
        user = split[1].split("/")[0]
    return user


if __name__ == '__main__':

    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument("--query", "-t", help="set topic search string")

    # Read arguments from the command line
    args = parser.parse_args()
    r = requests.get('https://paperswithcode.com/search?q_meta=&q_type=&q=' +
                     args.query)
    print(f"Fetching papers from url: {r.url}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        paper_url = []
        for a in soup.select('.entity > a'):
            if '#code' not in a['href']:
                paper_url.append('https://paperswithcode.com' + a['href'])

    print(f"Found following papers: {paper_url}")
    print("Fetching github users from papers...")

    github_url = []
    github_user = []
    SERVICE = "github.com"
    current_date = datetime.today().strftime('%Y-%m-%d')
    for url in paper_url:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')

            for a in soup.select('#implementations-full-list a'):
                if a['href'] != '#':
                    github_url.append(a['href'])
                    github_user.append([
                        SERVICE, current_date,
                        get_username_from_string(a['href'])
                    ])

    print(f"Found following users: {github_user}")

    pd.DataFrame(github_user,
                 columns=["service", "date",
                          "user_id"]).to_csv(Path("results",
                                                  "paperswithcode.csv"),
                                             index=False)
    print("Successfully exported users.")
