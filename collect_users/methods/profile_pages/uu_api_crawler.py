#pylint: skip-file
"""
This file retrieves Github usernames from the API of Utrecht University employee pages
"""
import time
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests

REST_API_URL = "https://www.uu.nl/medewerkers/RestApi/Public"


def get_employees_url(faculty_number):
    """The function takes a faculty number (0-99) and returns employee URLs

    Args:
        faculty_number (integer): Faculty number

    Returns:
        Series: Employee URLs retrieved from faculty
    """
    url = f"{REST_API_URL}/GetEmployeesOrganogram?f={faculty_number}&l=EN&fullresult=true"
    json_nested = requests.get(url)
    df_employees = pd.DataFrame(json_nested.json()["Employees"])
    try:
        return df_employees["Url"]
    except Exception as e: # pylint: disable=broad-except
        print(f"There was an error: {e}")
        return None


def get_all_employee_github_links(url):
    """Gathers all github links from a URL

    Args:
        url (string): URL

    Returns:
        List: Github links
    """
    time.sleep(1)
    try:
        api_link = requests.get(f"{REST_API_URL}/getEmployeeData?page={url}")
        api_json = api_link.json()
        git_link_list = []
        #try to retrieve from CV text
        if "CV" in api_json["Employee"].keys() and api_json["Employee"]["CV"]:
            employee_profile = api_json["Employee"]['CV']
            split_employee_profile = employee_profile.split()
            for word in split_employee_profile:
                if "github.com" in word:
                    split = word.split("github.com/")
                    # get value after "github.com/" and split after the next
                    # slash, then the first value of that split will be the
                    # username
                    user = split[1].split("/")[0]
                    # sometimes, there is still some tokens after the username
                    # due to the href format of the links. This is migated by
                    # splitting on a " and using the first word
                    user = user.split('"')[0]
                    git_link_list.append(user)
                elif "github.io" in word:
                    githubio_split = word.split(".")
                    try:
                        user = githubio_split[0].split("://")[1]
                    except Exception as e: # pylint: disable=broad-except
                        user = githubio_split[0]
                    # sometimes, there is still some tokens after the username
                    # due to the href format of the links. This is migated by
                    # splitting on a " and using the first word
                    user = user.split('"')[0]
                    git_link_list.append(user)

        if "Profile" in api_json["Employee"].keys(
        ) and api_json["Employee"]["Profile"]:
            employee_profile = api_json["Employee"]['Profile']
            split_employee_profile = employee_profile.split()
            for word in split_employee_profile:
                if "github.com" in word:
                    split = word.split("github.com/")
                    # get value after "github.com/" and split after the next
                    # slash, then the first value of that split will be the
                    # username
                    user = split[1].split("/")[0]
                    # sometimes, there is still some tokens after the username
                    # due to the href format of the links. This is migated by
                    # splitting on a " and using the first word
                    user = user.split('"')[0]
                    git_link_list.append(user)
                elif "github.io" in word:
                    githubio_split = word.split(".")
                    try:
                        user = githubio_split[0].split("://")[1]
                    except Exception as e: # pylint: disable=broad-except
                        user = githubio_split[0]
                    # sometimes, there is still some tokens after the username
                    # due to the href format of the links. This is migated by
                    # splitting on a " and using the first word
                    user = user.split('"')[0]
                    git_link_list.append(user)
        if "Links" in api_json["Employee"].keys(
        ) and api_json["Employee"]['Links']:
            employee_link_list = api_json["Employee"]['Links']
            for link_dict in employee_link_list:
                link = link_dict["Url"]
                if link:
                    if "github.com" in link:
                        split = link.split("github.com/")
                        # get value after "github.com/" and split after the
                        # next slash, then the first value of that split will
                        # be the username
                        user = split[1].split("/")[0]
                        git_link_list.append(user)
                    elif "github.io" in link:
                        githubio_split = link.split(".")
                        try:
                            user = githubio_split[0].split("://")[1]
                        except Exception as e: # pylint: disable=broad-except
                            user = githubio_split[0]
                        git_link_list.append(user)
        if len(git_link_list) != 0:
            return git_link_list
        else:
            return None
    except Exception as e: # pylint: disable=broad-except
        print(f"There was an error: {e}")
        return None


if __name__ == '__main__':

    employee_github_from_links = []
    employee_github_from_profile = []
    employee_github_from_cv = []
    employee_github = []
    SERVICE = "github.com"
    current_date = datetime.today().strftime('%Y-%m-%d')

    faculty_ids = []
    print(
        "Looping through faculties...",
        "Note: Getting errors here is expected. This will take a while.",
        "You can keep cancelling via ctrl + c until you see continuous errors."
    )
    for i in range(99):
        try:
            faculty_url = list(get_employees_url(i))
            print(i)
            try:
                for url in faculty_url:
                    github_user_names = get_all_employee_github_links(url)
                    if github_user_names:
                        for github_user_name in github_user_names:
                            employee_github.append(
                                [SERVICE, current_date, github_user_name])
            except Exception as e: # pylint: disable=broad-except
                print(f"couldn't loop through urls. Error: {e}")
                continue
        except Exception as e: # pylint: disable=broad-except
            print(f"error occured getting faculty url. Error: {e}")
            continue
    print("Finished looping through faculties.")
    employee_github_pd = pd.DataFrame(employee_github,
                                      columns=["service", "date", "user_id"])

    employee_github_pd = employee_github_pd.dropna()

    p = Path("results")
    p.mkdir(parents=True, exist_ok=True)

    employee_github_pd.to_csv(Path("results", "profile_page_uu.csv"),
                              index=False)
