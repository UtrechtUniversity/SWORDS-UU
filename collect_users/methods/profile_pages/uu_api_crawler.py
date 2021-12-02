import time
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests

REST_API_URL = "https://www.uu.nl/medewerkers/RestApi/Public"


def get_employees_url(faculty_number):
    url = f"{REST_API_URL}/GetEmployeesOrganogram?f={faculty_number}&l=EN&fullresult=true"
    json_nested = requests.get(url)
    df = pd.DataFrame(json_nested.json()["Employees"])
    try:
        return df["Url"]
    except:
        return None


def get_employee_links(url):
    time.sleep(1)
    API_link = requests.get(f"{REST_API_URL}/getEmployeeData?page={url}")
    API_json = API_link.json()

    try:
        return API_json["Employee"]['Links']
    except:
        return None


def get_employee_specific_link(url, search_query):
    time.sleep(1)
    API_link = requests.get(f"{REST_API_URL}/getEmployeeData?page={url}")
    API_json = API_link.json()

    try:
        employee_link_list = API_json["Employee"]['Links']
        for link in employee_link_list:
            if search_query in link['Url']:
                return link['Url']
        return None
    except:
        return None


def get_employee_github_from_links(url):
    time.sleep(1)
    API_link = requests.get(f"{REST_API_URL}/getEmployeeData?page={url}")
    API_json = API_link.json()

    try:
        employee_link_list = API_json["Employee"]['Links']
        for link_dict in employee_link_list:
            link = link_dict["Url"]
            if "github.com" in link:
                split = link.split("github.com/")
                # get value after "github.com/" and split after the next
                # slash, then the first value of that split will be the
                # username
                user = split[1].split("/")[0]
                return user
            elif "github.io" in link:
                githubio_split = link.split(".")
                user = githubio_split[0].split("://")[1]
                return user
        return None
    except:
        return None


def get_employee_profile_mention(url, query):
    query = query.lower()
    time.sleep(1)
    API_link = requests.get(f"{REST_API_URL}/getEmployeeData?page={url}")
    API_json = API_link.json()

    try:
        employee_profile = API_json["Employee"]['Profile']
        if query in employee_profile.lower():
            return f"{query} found in user profile"
        return None
    except:
        return None


def get_employee_github_from_profile(url):
    time.sleep(1)
    API_link = requests.get(f"{REST_API_URL}/getEmployeeData?page={url}")
    API_json = API_link.json()
    try:
        employee_profile = API_json["Employee"]['Profile']
        split_employee_profile = employee_profile.split()
        for word in split_employee_profile:
            if "github.com" in word:
                split = word.split("github.com/")
                # get value after "github.com/" and split after the next
                # slash, then the first value of that split will be the
                # username
                user = split[1].split("/")[0]
                # sometimes, there is still some tokens after the username due
                # to the href format of the links. This is migated by
                # splitting on a " and using the first word
                user = user.split('"')[0]
                return user
            elif "github.io" in word:
                githubio_split = word.split(".")
                user = githubio_split[0].split("://")[1]
                # sometimes, there is still some tokens after the username due
                # to the href format of the links. This is migated by
                # splitting on a " and using the first word
                user = user.split('"')[0]
                return user
        return None
    except:
        return None


def get_employee_github_from_cv(url):
    time.sleep(1)
    API_link = requests.get(f"{REST_API_URL}/getEmployeeData?page={url}")
    API_json = API_link.json()
    try:
        employee_profile = API_json["Employee"]['CV']
        split_employee_profile = employee_profile.split()
        for word in split_employee_profile:
            if "github.com" in word:
                split = word.split("github.com/")
                # get value after "github.com/" and split after the next
                # slash, then the first value of that split will be the
                # username
                user = split[1].split("/")[0]
                # sometimes, there is still some tokens after the username due
                # to the href format of the links. This is migated by
                # splitting on a " and using the first word
                user = user.split('"')[0]
                return user
            elif "github.io" in word:
                githubio_split = word.split(".")
                user = githubio_split[0].split("://")[1]
                # sometimes, there is still some tokens after the username due
                # to the href format of the links. This is migated by
                # splitting on a " and using the first word
                user = user.split('"')[0]
                return user
        return None
    except:
        return None


def get_all_employee_github_links(url):
    time.sleep(1)
    try:
        API_link = requests.get(f"{REST_API_URL}/getEmployeeData?page={url}")
        API_json = API_link.json()
        git_link_list = []
        #try to retrieve from CV text
        if "CV" in API_json["Employee"].keys() and API_json["Employee"]["CV"]:
            employee_profile = API_json["Employee"]['CV']
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
                    except:
                        user = githubio_split[0]
                    # sometimes, there is still some tokens after the username
                    # due to the href format of the links. This is migated by
                    # splitting on a " and using the first word
                    user = user.split('"')[0]
                    git_link_list.append(user)

        if "Profile" in API_json["Employee"].keys(
        ) and API_json["Employee"]["Profile"]:
            employee_profile = API_json["Employee"]['Profile']
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
                    except:
                        user = githubio_split[0]
                    # sometimes, there is still some tokens after the username
                    # due to the href format of the links. This is migated by
                    # splitting on a " and using the first word
                    user = user.split('"')[0]
                    git_link_list.append(user)
        if "Links" in API_json["Employee"].keys(
        ) and API_json["Employee"]['Links']:
            employee_link_list = API_json["Employee"]['Links']
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
                        except:
                            user = githubio_split[0]
                        git_link_list.append(user)
        if len(git_link_list) != 0:
            return git_link_list
        else:
            return None
    except:
        return None


if __name__ == '__main__':

    employee_github_from_links = []
    employee_github_from_profile = []
    employee_github_from_cv = []
    employee_github = []
    service = "github.com"
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
                                [service, current_date, github_user_name])
            except:
                print("couldn't loop through urls")
                continue
        except:
            print("error occured getting faculty url")
            continue
    print("Finished looping through faculties.")
    employee_github_pd = pd.DataFrame(employee_github,
                                      columns=["service", "date", "user_id"])

    employee_github_pd = employee_github_pd.dropna()

    p = Path("results")
    p.mkdir(parents=True, exist_ok=True)

    employee_github_pd.to_csv(Path("results", "profile_page_uu.csv"),
                              index=False)
