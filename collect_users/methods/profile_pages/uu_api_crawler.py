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
    request_url = f"{REST_API_URL}/GetEmployeesOrganogram?f={faculty_number}&l=EN&fullresult=true"
    json_nested = requests.get(request_url)
    df_employees = pd.DataFrame(json_nested.json()["Employees"])
    try:
        return df_employees["Url"]
    except Exception as ex: # pylint: disable=broad-except
        print(f"There was an error: {ex}")
        return None



def parse_string_list_for_github_name(words):
    """Gathers all github names from a list of strings

    Args:
        words (list): a list of strings.
        Example: ["<p>I'm", 'a', 'community', 'organizer', 'and', 'research', 'engineer']

    Returns:
        List: GitHub names
    """
    matches = []
    for word in words:
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
            matches.append(user)
        elif "github.io" in word:
            githubio_split = word.split(".")
            try:
                user = githubio_split[0].split("://")[1]
            except Exception: # pylint: disable=broad-except
                user = githubio_split[0]
            # sometimes, there is still some tokens after the username
            # due to the href format of the links. This is migated by
            # splitting on a " and using the first word
            user = user.split('"')[0]
            matches.append(user)
    return matches


def parse_urls_for_github_name(employee_urls):
    """Gathers all github names from the social media links of an employee

    Args:
        employee_urls (list): a list of dicts containing info about links.
        Example: [{'Name': 'Github', 'Url': 'https://github.com/kequach'}]

    Returns:
        List: GitHub names
    """
    matches = []
    for link_dict in employee_urls:
        link = link_dict["Url"]
        if link:
            if "github.com" in link:
                split = link.split("github.com/")
                # get value after "github.com/" and split after the
                # next slash, then the first value of that split will
                # be the username
                user = split[1].split("/")[0]
                matches.append(user)
            elif "github.io" in link:
                githubio_split = link.split(".")
                try:
                    user = githubio_split[0].split("://")[1]
                except Exception: # pylint: disable=broad-except
                    user = githubio_split[0]
                matches.append(user)
    return matches


def get_all_employee_github_usernames(user_id):
    """Gathers all github links from a URL

    Args:
        user_id (string): UU employee id

    Returns:
        List: Github links
    """
    time.sleep(1)
    try:
        api_link = requests.get(f"{REST_API_URL}/getEmployeeData?page={user_id}")
        api_json = api_link.json()
        git_link_list = []
        #try to retrieve from CV text
        if "CV" in api_json["Employee"].keys() and api_json["Employee"]["CV"]:
            employee_profile = api_json["Employee"]['CV']
            split_employee_profile = employee_profile.split()
            github_names = parse_string_list_for_github_name(split_employee_profile)
            if github_names:
                git_link_list.extend(github_names)

        if "Profile" in api_json["Employee"].keys() and api_json["Employee"]["Profile"]:
            employee_profile = api_json["Employee"]['Profile']
            split_employee_profile = employee_profile.split()
            github_names = parse_string_list_for_github_name(split_employee_profile)
            if github_names:
                git_link_list.extend(github_names)

        if "Links" in api_json["Employee"].keys() and api_json["Employee"]['LinksSocialMedia']:
            links_social_media = api_json["Employee"]['LinksSocialMedia']
            github_names = parse_urls_for_github_name(links_social_media)
            if github_names:
                git_link_list.extend(github_names)

        if len(git_link_list) != 0:
            return list(set(git_link_list))
        return None
    except Exception as ex: # pylint: disable=broad-except
        print(f"There was an error: {ex}")
        return None


if __name__ == '__main__':

    COUNTER = 0
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
            faculty_employee_ids = list(get_employees_url(i))
            print(f"Parsing faculty number {i}")
            try:
                for employee_id in faculty_employee_ids:
                    github_user_names = get_all_employee_github_usernames(employee_id)
                    if github_user_names:
                        for github_user_name in github_user_names:
                            COUNTER += 1
                            print(f"Found user: '{github_user_name}'. \
                                  Employee ID: '{employee_id}'. Total: {COUNTER}")
                            employee_github.append(
                                [SERVICE, current_date, github_user_name, employee_id])
            except Exception as e: # pylint: disable=broad-except
                print(f"couldn't loop through urls. Error: {e}")
                continue
        except Exception as e: # pylint: disable=broad-except
            print(f"error occured getting faculty url. Error: {e}")
            continue
    print("Finished looping through faculties.")
    employee_github_pd = pd.DataFrame(employee_github,
                                      columns=["service", "date", "user_id", "UU_id"])

    employee_github_pd = employee_github_pd.dropna()

    p = Path("results")
    p.mkdir(parents=True, exist_ok=True)

    employee_github_pd.to_csv(Path("results", "profile_page_uu.csv"),
                              index=False)
