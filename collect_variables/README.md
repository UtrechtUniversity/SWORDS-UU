# Variable collection <!-- omit in toc -->

- [Installation](#installation)
- [Usage](#usage)
  - [Gather howfairis variables](#gather-howfairis-variables)
  - [Gather GitHub variables as tidy data](#gather-github-variables-as-tidy-data)
  - [Data analysis](#data-analysis)
- [License](#license)
- [Contact](#contact)

<img src="../docs/Phase_3.png" height="500">

This submodule of the SWORDS project is used to collect GitHub repositories from users that were collected in the previous phase. 

## Installation 

The code in this submodule requires Python 3.7+. To install the code dependencies for the data analysis, install the packages in the requirements file. Each variable collection has its own requirements.txt file to allow only necessary dependencies to be installed.

```console
pip install -r scripts/github_api/requirements.txt
pip install -r scripts/howfairis/requirements.txt
pip install -r requirements.txt
```

## Usage

### Gather howfairis variables

In this step, howfairis variables are retrieved. To do this, execute the file **howfairis_variables.py**. Note: The output concatenates the howfairis variables to the whole repository data. By doing so, it is possible to reuse this file to gather GitHub variables based on this file.
There are 2 arguments that can be passed. Bold arguments are required:

- --**input**: The file name of the repositories.
- --output: The file name of the output. Note that there will always be a timestamp added to the file name in the following format: YYYY-MM-DD. Default value: output/repositories_howfairis

Navigate to this folder and execute the script. Adjust parameters as needed. Example:

```console
python scripts/howfairis/howfairis_variables.py --input ../collect_repositories/results/repositories_filtered_2021-11-04.csv
python scripts/howfairis/howfairis_variables.py --input ../collect_repositories/results/repositories_filtered_2021-11-04.csv --output output/repositories_howfairis_duplicate
```

### Gather GitHub variables as tidy data

In this step, additional variables from repositories are retrieved. These include information about contributors, used languages, jupyter notebook file paths and topics in tidy data format. To do this, execute the file **github.py**.
There are 10 arguments that can be passed. For each of the 4 information types you can set a flag if you want to retrieve this information, as well as the file output path which is optional. In addition, the jupyter notebooks require an additional argument to specify an input file for the languages (output file of languages) in case languages is not also retrieved. See examples. Bold arguments are required:

- --**input**: The file name of the repositories data. This can also be the output from the previous howfairis step.
- --contributors: Set this flag if contributors should be retrieved
- --contributors_output: Optional. Path for contributors output. Default: output/contributors
- --jupyter: Set this flag if jupyter notebooks should be retrieved
- --input_languages: Optional. If languages are not retrieved but jupyter notebooks should be, there needs to be an input file with the languages.
- --jupyter_output: Optional. Path for jupyter notebooks output. Default: output/jupyter_notebooks
- --languages: Set this flag if languages should be retrieved
- --languages_output: Optional. Path for languages output. Default: output/languages
- --topics: Set this flag if topics should be retrieved
- --topics_output: Optional. Path for topics output. Default: output/topics


Navigate to this folder and execute the script. Adjust parameters as needed. Example:

```console
python scripts/github_api/github.py --input ../collect_repositories/results/repositories_filtered_2021-11-04.csv --contributors --contributors_output output/contributors
python scripts/github_api/github.py --input output/repositories_howfairis_2021-11-04.csv --contributors --languages --jupyter --topics
python scripts/github_api/github.py --input output/repositories_howfairis_2021-11-04.csv --jupyter --input_languages output/languages_2021-11-04.csv
```

### Data analysis

Interactive data analysis can be found in the [Jupyter Notebook variable_analysis.ipynb](variable_analysis.ipynb). As mentioned in the phase diagram, it is possible to optionally filter the analysis for research groups or private users only. This is elaborated in the Jupyter notebook.

## License

See [/LICENSE](../LICENSE).

## Contact

See https://github.com/UtrechtUniversity/SWORDS-UU.