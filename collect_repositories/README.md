# Repository collection <!-- omit in toc -->

- [Installation](#installation)
- [Usage](#usage)
  - [Retrieve repositories of filtered users](#retrieve-repositories-of-filtered-users)
  - [Filter repositories](#filter-repositories)
  - [Data analysis](#data-analysis)
- [License](#license)
- [Contact](#contact)

<img src="../docs/Phase_2.png" height="500">

This submodule of the SWORDS project is used to collect GitHub repositories from users that were collected in the previous phase. 

## Installation 

The code in this submodule requires Python 3.7+. To install the code dependencies, install the packages in the requirements file. 

```console
pip install -r requirements.txt
```

## Usage

### Retrieve repositories of filtered users

In this step, repositories of enriched users are retrieved. To do this, execute the file **repositories.py**. Note: The column with githuber user ids needs to have the name **user_id**.
There are 2 arguments that can be passed.

- --users: The path to the file with enriched users. Default value: ../collect_users/results/unique_users_annotated.xlsx
- --output: The file name of the repositories that are retrieved. Note that there will always be a timestamp added to the file name in the following format: YYYY-MM-DD. Default value: results/repositories

Navigate to this folder and execute the script. Adjust parameters as needed. Example:

```console
python scripts/repositories.py --users ../collect_users/results/unique_users_annotated.xlsx --output results/repositories
```

### Filter repositories

In this step, non-relevant repositories are filtered. To do this, execute the file **filter_repos.py**.
There are 2 arguments that can be passed. Bold arguments are required:

- --**input**: The file name of the retrieved repositories.
- --output: The file name of the filtered repositories. Note that there will always be a timestamp added to the file name in the following format: YYYY-MM-DD. Default value: repositories_filtered

Navigate to this folder and execute the script. Adjust parameters as needed. Example:

```console
python scripts/filter_repos.py --input results/repositories_2021-11-04.csv 
```

Currently, the script only filters out *github.io* repositories, as these are usually no research repositories. Additional filtering can be done manually.

### Data analysis

Interactive data analysis can be found in the [Jupyter Notebook analyse_repositories.ipynb](analyse_repositories.ipynb). It is possible to optionally filter the analysis for research groups or private users only. This is elaborated in the Jupyter notebook.

This notebook analyzes the information of the retrieved repositories. The notebook contains analysis of open science mentions, stargazers, watchers, issues, forks, branches, homepages and commits.

## License 

See [/LICENSE](../LICENSE).

## Contact 

See https://github.com/UtrechtUniversity/SWORDS-UU.