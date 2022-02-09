# GitHub User Search

ghapi package - github_search retrieves all users for the following: 
* owners of repositories that appear for the query under the **topic** argument
* owners of repositories that appear for the query of the **search** argument
* users that appear for the query of the **search** argument

## Installation

To use this submodule, install the requirements with 

```console
pip install -r requirements.txt
```

## Usage

First, navigate to this folder. Then, execute the script with arguments. For example:

```console
python github_search.py --topic utrecht-university --search "utrecht university"
```

The collected GitHub user identifiers are stored in the results folder. 

## License

See [LICENSE](../../LICENSE).

## Contact

See [here](../../README.md#contact).