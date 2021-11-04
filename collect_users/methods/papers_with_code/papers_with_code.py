import requests
from pathlib import Path
import argparse

from bs4 import BeautifulSoup
import pandas as pd


def get_username_from_string(url):
    if "github.com" in url:
        split = url.split("github.com/")
        # get value after "github.com/" and split after the next slash, then the first value of that split will be the username
        user = split[1].split("/")[0]
        return user
    else:
        return None


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
            if ('#code' not in a['href']):
                paper_url.append('https://paperswithcode.com' + a['href'])

    print(f"Found following papers: {paper_url}")
    print(f"Fetching github users from papers...")

    github_url = []
    github_user = []
    for url in paper_url:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')

            for a in soup.select('#implementations-full-list a'):
                if ('#' != a['href']):
                    github_url.append(a['href'])
                    github_user.append(get_username_from_string(a['href']))

    print(f"Found following github users: {github_user}")

    pd.Series(github_user,
              name="github_user_id").to_csv(Path("results",
                                                 "ids_paperswithcode.csv"),
                                            index=False)
    print("Successfully exported users.")
