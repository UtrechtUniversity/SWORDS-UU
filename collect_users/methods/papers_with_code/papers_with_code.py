"""
This file retrieves Github usernames from PapersWithCode.com
"""
import argparse
from pathlib import Path
from datetime import datetime

import pandas as pd
from paperswithcode import PapersWithCodeClient


if __name__ == '__main__':

    # Initiate the parser
    parser = argparse.ArgumentParser()

    # Add arguments to be parsed
    parser.add_argument("--query", "-t", help="set topic search string")
    SERVICE = "github.com"
    current_date = datetime.today().strftime('%Y-%m-%d')

    # Read arguments from the command line
    args = parser.parse_args()
    client = PapersWithCodeClient()
    query_result = client.search(q=args.query, items_per_page=100).results
    result = []
    paper_title = []
    for paper in query_result:
        paper_title.append(paper.paper.title)
        result.append([SERVICE, current_date, paper.repository.owner])

    print(f"Found following papers: {paper_title}")
    print(f"Found following users: {[user[2] for user in result]}")

    pd.DataFrame(result,
                 columns=["service", "date",
                          "user_id"]).to_csv(Path("results",
                                                  "paperswithcode.csv"),
                                             index=False)
    print("Successfully exported users.")
