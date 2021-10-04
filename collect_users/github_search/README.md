# GitHub User Search

ghapi package - github_search retrieves all users for the following: 
* owners of repositories that have the "utrecht-university" tag
* owners of repositories that appear on the search of "utrecht university"
* users that appear on the search of "utrecht university"

## Installation

To use this submodule, install the requirements with 

```
pip install requirements.txt
```

## Usage

First, navigate to this folder. Then, execute the script with arguments.
```
python github_search.py --topic utrecht-university --search "utrecht university"
```

The collected GitHub user identifiers are stored in the results folder. 

## License

See [LICENSE](../../LICENSE).

## Contact

See https://github.com/UtrechtUniversity/SWORDS-UU.