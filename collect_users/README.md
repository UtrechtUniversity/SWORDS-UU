# User collection

This submodule of the SWORDS project is used to collect user profiles from
GitHub and GitLab that match the given criteria. 

Currently, the following collection methods are available: 

- PapersWithCode
- GitHub Search
- Pure

## Installation 

The code in this submodule requires Python 3.7+. To install the code dependencies, install the packages in the requirements file. 

```
pip install -r github_search/requirements.txt
```

## Usage

See each individual user collection method for usage instructions. Each method
stores the collected user profiles in the `results` folder. 

Because there are multiple user collection methods, users can be found with
multiple methods. Therefore, the collected data is deduplicated after
collection. 

The structure of the data is as follows:

```

```

## License 

See [/LICENSE](LICENSE).

## Contact 

See https://github.com/UtrechtUniversity/SWORDS-UU.