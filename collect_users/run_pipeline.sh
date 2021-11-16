#!/bin/bash
echo "Fetching users..."
cd methods/github_search
pip install -r requirements.txt
python github_search.py --topic utrecht-university --search "utrecht university"
cd ../papers_with_code
pip install -r requirements.txt
python papers_with_code.py --query utrecht+university
cd ../pure
pip install -r requirements.txt
python pure.py
cd ../profile_pages
pip install -r requirements.txt
python uu_api_crawler.py
echo "Merging users..."
pip install -r requirements.txt

cd ../../
python scripts/merge_users.py --files methods/*/results/*.csv --output results/users_merged.csv
echo "Enriching users..."
python scripts/enrich_users.py --input results/users_merged.csv
echo "Preparing user filtering..."
python scripts/prepare_filtering.py
echo "Pipeline run succeeded."