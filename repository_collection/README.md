# Manual for repository collection
The data was retrieved on the following date: 29.04.2021 (DD/MM/YYYY)

## Installation

Install the necessary requirements for each retrieval method through the requirements.txt in the corresponding folder with the following command

```bash
pip install -r requirements.txt
```

## Usage

1. Execute the scripts in the subfolders **github_search**, **pure** and **university_profile_pages** in arbitrary sequence:
    ```bash
    python3 repository_collection/github_search/github_search.py
    python3 repository_collection/pure/pure.py
    python3 repository_collection/university_profile_pages/uu_api_crawler.py
    ```
    Note that **papers_with_code** results were collected manually due to only 4 papers being available.

    The result will be located in each subfolder within a results subfolder where .csv files are generated. 

2. Then, go through the ***merge_github_user_profiles*** Jupyter notebook to merge all results.
    Note that you need to create a .env file and add the following line:
    ```GITHUB_TOKEN = "YOUR_PERSONAL_GITHUB_TOKEN" ```
    See here on how to create a Github token: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token 
    Since the Github API is limiting the number of unauthorized requests quite a lot, this is necessary to decrease duration of the overall runtime. The result will be a .csv file with all unique users.
3. Execute the script found in the **get_repositories** subfolder:
    ```bash
    python3 repository_collection/get_repositories/repositories.py
    ```
    The result will be a .csv file in the folder repository_collection with all repositories of the unique users.
