#!/bin/bash
echo "Fetching users..."
cd methods/github_search
pip -q install -r requirements.txt
python github_search.py --topic utrecht-university --search "utrecht university"
echo "Github search method finished."
cd ../papers_with_code
pip -q install -r requirements.txt
python papers_with_code.py --query utrecht+university
echo "PapersWithCode search method finished."
cd ../pure
pip -q install -r requirements.txt
python pure.py data/Pure_290421.ris
echo "PURE search method finished."
cd ../profile_pages
pip -q install -r requirements.txt
echo "Starting UU API search method. This will take a while."
python uu_api_crawler.py
echo "UU API search method finished."
echo "Merging users..."

cd ../../
pip -q install -r requirements.txt
python scripts/merge_users.py --files methods/*/results/*.csv --output results/users_merged.csv
echo "Enriching users..."
python scripts/enrich_users.py --input results/users_merged.csv
echo "Preparing user filtering..."
python scripts/prepare_filtering.py
echo "Pipeline run succeeded."