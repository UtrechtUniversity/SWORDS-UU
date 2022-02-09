# User collection

<img src="../docs/Phase_1.png" height="500">

This submodule of the SWORDS framework is used to collect user profiles from
GitHub and GitLab that are related to the organisation.

Currently, the following user collection methods are available:

- **[PapersWithCode](methods/papers_with_code)** The website Papers With Code (https://paperswithcode.com/) highlights Machine Learning research and the code to implement it. 
- **[GitHub Search](methods/github_search)** Search for users on [GitHub Search](https://github.com/search/advanced) based on tags, users, and repositories given references to the organisation.
- **[Research Information Management System (RIMS)](methods/pure)** Use the Research Information Management System of the organisation, PURE https://www.elsevier.com/solutions/pure, for collection of research software and code. 
- **[Employee pages](methods/profile_pages)** Collect user profiles from the Utrecht University website.

The collection method scripts can be found in the subfolder `methods`. Each method has a subfolder `results` where the output will be located.

The merging, enriching and preparation for filtering scripts can be found in the `scripts` subfolder. The output from these can be found in the `results` subfolder.

## Installation

The code in this submodule requires Python 3.7+. To install the code dependencies, install the packages in the requirements file. This covers requirements for files in the *scripts* folder, as well as the data analysis notebook. For the collection methods, each collection method has its own requirements.txt file in the corresponding subfolder.

```console
pip install -r requirements.txt
```

## Usage

### Running whole phase 1 pipeline

There is a shell script **run_pipeline.sh** available that will run all the necessary steps. Otherwise you can execute each of them on its own. Please note that you can change the arguments in the shell script to your needs.

To use it, navigate to this folder and run the file. On windows, you can use Git Bash to execute it.

### Gather GitHub user profiles from data sources

See each individual user collection method for usage instructions. Each method
stores the collected user profiles in the `results` folder in the schema of the following example:

| service    | date       | user_id  |
| ---------- | ---------- | -------- |
| github.com | 2021-12-02 | kequach  |
| github.com | 2021-12-02 | J535D165 |

Currently, only github.com data is retrieved. This project can be extended to other services like GitLab.

### Merge users to CSV file

Because there are multiple user collection methods, users can be found with
multiple methods. Therefore, the collected data is deduplicated after
collection.

Note that you should create a `.env` file in the root project folder and add the following lines:
```
GITHUB_TOKEN = "YOUR_PERSONAL_GITHUB_TOKEN" 
GITHUB_USER = "YOUR_GITHUB_USERNAME" 
```
See here on how to create a Github token: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
Since the Github API is limiting the number of unauthorized requests quite a lot, this is recommended to decrease the runtime. Otherwise the waiting time is much longer.

Users from each collection method need to be merged after each method was executed. To do this, execute the file **merge_users.py**.
There are 2 arguments that can be passed.

- `--files`: The query for merging the .csv files. To merge all CSV files in each results folder, use the following query (this is the default): `methods/*/results/*.csv`
  - You can add multiple arguments to specify specific files or also to use wildcards as shown in the default. See examples.
- `--output`: The file name of the merged output. Default value: `results/users_merged.csv`

Navigate to this folder and execute the script. Adjust parameters as needed. Example:

```console
python scripts/merge_users.py --files methods/*/results/*.csv --output results/users_merged.csv
python scripts/merge_users.py --files methods/*/results/*.csv additional_users.csv --output results/users_merged.csv
```

The structure of the exported data is as follows:

```
user_id,source,service,timestamp
```

Where source indicates from which method the user id was retrieved.

### Enrich users with GitHub data

Next, the data is enriched with GitHub information. Execute the file **enrich_users.py**.
 Note: This script can also be used to update users of an existing file, as well as adding additional users. It can be specified whether the update should only include new entries (e.g. when there are more results available) or if all users should be updated.
There are 4 arguments that can be passed.

- `--input`: The file name of the input. Default: `results/users_merged.csv`
- `--update`: Boolean flag. Update everything including existing users or only add new users. Only relevant if fileupdate argument is provided. This is false by default.
- `--fileupdate`: If you want to update an existing file, provide a file name in this argument. Example: `results/unique_users_annotated.xlsx`
- `--output`: The file name of the enriched output. Default: `results/users_enriched.csv`

Navigate to this folder and execute the script. Adjust parameters as needed. Examples:

```console
python scripts/enrich_users.py --input results/users_merged.csv --output results/users_enriched.csv
python scripts/enrich_users.py --input results/users_merged.csv --fileupdate results/users_enriched.csv
python scripts/enrich_users.py --input results/users_merged.csv --update --fileupdate results/users_enriched.csv --output results/users_enriched_updated.csv
```

### Prepare filtering

Next, preparation for manual filtering will be done. In this step, a flag whether a user is a student will be added based on information provided in the biography, as well as empty columns that will be filled out in the next step: is_employee, is_currently_employed, is_research_group, final_decision, note.

Execute the file `prepare_filtering.py`.
There are 2 arguments that can be passed.

- `--input`: The file name of the input. Default: `results/users_enriched.csv`
- `--output`: The file name of the enriched output. Default: `results/users_enriched.csv`

Navigate to this folder and execute the script. Adjust parameters as needed. Examples:

```console
python scripts/prepare_filtering.py
```

### Filter users

The filtering of users is done manually. It is recommended to turn the resulting file from the previous step to an XLSX file and make use of Excel tools to manually annotate the users. In the SWORDS@UU implementation, we decided to filter out students in this step. The resulting file was named `unique_users_annotated.xlsx` which is assumed to be the file used as input for phase 2.

### Data analysis

Interactive data analysis can be found in the [Jupyter Notebook analyze_users.ipynb](analyze_users.ipynb). This notebook explores the data sources that were used to collect the repositories.

## License

See [/LICENSE](../LICENSE).

## Contact

See [here](../README.md#contact).