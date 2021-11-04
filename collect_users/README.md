# User collection <!-- omit in toc -->

- [Installation](#installation)
- [Usage](#usage)
  - [Gather GitHub user profiles from data sources](#gather-github-user-profiles-from-data-sources)
  - [Merge users to CSV file](#merge-users-to-csv-file)
  - [Enrich users with GitHub data](#enrich-users-with-github-data)
  - [Prepare filtering](#prepare-filtering)
  - [Filter users](#filter-users)
  - [Data analysis](#data-analysis)
- [License](#license)
- [Contact](#contact)

<img src="../docs/Phase_1.png" height="500">

This submodule of the SWORDS project is used to collect user profiles from
GitHub and GitLab that match the given criteria. 

Currently, the following collection methods are available: 

- PapersWithCode
- GitHub Search
- Pure
- UU employee pages

The collection method scripts can be found in the subfolder *methods*. Each method has a subfolder *results* where the output will be located. 

The merging, enriching and preparation for filtering scripts can be found in the *scripts* subfolder. The output from these can be found in the *results* subfolder.

## Installation 

The code in this submodule requires Python 3.7+. To install the code dependencies, install the packages in the requirements file. This covers requirements for files in the *scripts* folder, as well as the data analysis notebook. For the collection methods, each collection method has its own requirements.txt file in the corresponding subfolder.

```console
pip install -r requirements.txt
```

## Usage

### Gather GitHub user profiles from data sources

See each individual user collection method for usage instructions. Each method
stores the collected user profiles in the `results` folder. 

### Merge users to CSV file

Because there are multiple user collection methods, users can be found with
multiple methods. Therefore, the collected data is deduplicated after
collection. 

Users from each collection method need to be merged after each method was executed. To do this, execute the file **merge_users.py**.
There are 2 arguments that can be passed.

- --files: The query for merging the .csv files. To merge all .csv files in each results folder, use the following query (this is the default): methods/*/results/*.csv
- --output: The file name of the merged output. Default value: results/users_merged.csv

Navigate to this folder and execute the script. Adjust parameters as needed. Example:

```console
python scripts/merge_users.py --files methods/*/results/*.csv --output results/users_merged.csv
```

The structure of the exported data is as follows:

```
github_user_id,source
```

Where source indicates from which method the user id was retrieved.

### Enrich users with GitHub data

Next, the data is enriched with GitHub information. Execute the file **enrich_users.py**.
 Note: This script can also be used to update an existing file. It can also be specified whether the update should only include new entries (e.g. when there are more results available) or if everything should be updated.
There are 4 arguments that can be passed.

- --input: The file name of the input. Default: results/users_merged.csv
- --update: Boolean flag. Update everything including existing users or only add new users. Only relevant if fileupdate argument is provided. This is false by default.
- --fileupdate: If you want to update an existing file, provide a file name in this argument. Example: results/unique_users_annotated.xlsx
- --output: The file name of the enriched output. Default: results/users_enriched.csv

Navigate to this folder and execute the script. Adjust parameters as needed. Examples:

```console
python scripts/enrich_users.py --input results/users_merged.csv
python scripts/enrich_users.py --input results/users_merged.csv --fileupdate results/users_enriched.csv
python scripts/enrich_users.py --input results/users_merged.csv --update --fileupdate results/users_enriched.csv --output results/users_enriched_updated.csv
```

### Prepare filtering

Next, preparation for manual filtering will be done. In this step, a flag whether a user is a student will be added based on information provided in the biography, as well as empty columns that will be filled out in the next step: is_employee, is_currently_employed, is_research_group, final_decision, note.

Execute the file **prepare_filtering.py**.
There are 2 arguments that can be passed.

- --input: The file name of the input. Default: results/users_enriched.csv
- --output: The file name of the enriched output. Default: results/users_enriched.csv

Navigate to this folder and execute the script. Adjust parameters as needed. Examples:

```console
python scripts/prepare_filtering.py
```

### Filter users

The filtering of users is done manually. It is recommended to turn the resulting file from the previous step to an .xlsx file and make use of Excel tools to manually annotate the users. In the SWORDS UU implementation, we decided to filter out students in this step.

### Data analysis

Interactive data analysis can be found in the [Jupyter Notebook analysis_of_data_sources.ipynb](analysis_of_data_sources.ipynb).

## License 

See [/LICENSE](../LICENSE).

## Contact 

See https://github.com/UtrechtUniversity/SWORDS-UU.