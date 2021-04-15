import json
import time
from pathlib import Path

import pandas as pd
import requests


def get_employees_url(faculty_number):
    url = f"https://www.uu.nl/medewerkers/RestApi/Public/GetEmployeesOrganogram?f={faculty_number}&l=EN&fullresult=true"
    json_nested  = requests.get(url)
    df = pd.DataFrame(json_nested.json()["Employees"])
    return df["Url"]


def get_employee_links(url):
    time.sleep(1)#avoid ban by adding time between requests
    API_link = requests.get(f"https://www.uu.nl/medewerkers/RestApi/Public/getEmployeeData?page={url}")
    API_json = API_link.json()

    try:#try if a key exists for links of the employee
        return  API_json["Employee"]['Links']
    except:
        return None


def get_employee_specific_link(url, search_query):
    time.sleep(1)#avoid ban by adding time between requests
    API_link = requests.get(f"https://www.uu.nl/medewerkers/RestApi/Public/getEmployeeData?page={url}")
    API_json = API_link.json()

    try:#try if a key exists for links of the employee
        employee_link_list =  API_json["Employee"]['Links']
        for link in employee_link_list:
            if  search_query in link['Url']:
                return link['Url']
        return None
    except:
        return None


def get_employee_github_from_links(url):
    time.sleep(1)#avoid ban by adding time between requests
    API_link = requests.get(f"https://www.uu.nl/medewerkers/RestApi/Public/getEmployeeData?page={url}")
    API_json = API_link.json()

    try:#try if a key exists for links of the employee
        employee_link_list =  API_json["Employee"]['Links']
        for link in employee_link_list:
            if "github" in link['Url']:
                return link['Url']
        return None
    except:
        return None


def get_employee_profile_mention(url, query):
    query = query.lower() # Casing doesn't matter for search
    time.sleep(1)#avoid ban by adding time between requests
    API_link = requests.get(f"https://www.uu.nl/medewerkers/RestApi/Public/getEmployeeData?page={url}")
    API_json = API_link.json()

    try:#try if a key exists for profile of the employee
        employee_profile =  API_json["Employee"]['Profile']
        if query in employee_profile.lower():
            return f"{query} found in user profile"
        return None
    except:
        return None
def get_employee_github_from_profile(url):
    time.sleep(1)#avoid ban by adding time between requests
    API_link = requests.get(f"https://www.uu.nl/medewerkers/RestApi/Public/getEmployeeData?page={url}")
    API_json = API_link.json()
    try:#try if a key exists for profile of the employee
        employee_profile =  API_json["Employee"]['Profile']
        #print(employee_profile)
        split_employee_profile = employee_profile.split()
        for word in split_employee_profile:
            if "github.com" in word:
                if "href=" in word:
                    return word.replace("href=", "")
                return word
            elif "github.io" in word:
                githubio_split = word.split(".")
                return "github.com/" + githubio_split[0]
        return None
    except:
        return None
def get_employee_github_from_cv(url):
    time.sleep(1)#avoid ban by adding time between requests
    API_link = requests.get(f"https://www.uu.nl/medewerkers/RestApi/Public/getEmployeeData?page={url}")
    API_json = API_link.json()
    try:#try if a key exists for profile of the employee
        employee_profile =  API_json["Employee"]['CV']
        #print(employee_profile)
        split_employee_profile = employee_profile.split()
        for word in split_employee_profile:
            if "github.com" in word:
                if "href=" in word:
                    return word.replace("href=", "")
                return word
            elif "github.io" in word:
                githubio_split = word.split(".")
                return "github.com/" + githubio_split[0].replace("https://", "")
        return None
    except:
        return None





#employee_links = []
#employee_link_query = []
#employee__profile_query = []
employee_github_from_links = []
employee_github_from_profile = []
employee_github_from_cv = []

all_urls = list(get_employees_url(5))

for url in all_urls:
    employee_github_from_links.append([url, get_employee_github_from_links(url)])
    employee_github_from_cv.append([url, get_employee_github_from_cv(url)])
    employee_github_from_profile.append([url, get_employee_github_from_profile(url)])
    #employee_links.append([url, get_employee_links(url)])
    #employee_link_query.append([url, get_employee_specific_link(url, "orcid")])
    #employee__profile_query.append([url, get_employee_profile_mention(url, "open science")])

employee_github_from_links_pd = pd.DataFrame(employee_github_from_links,  columns=["uu_user_id", "github_user_url"])
employee_github_from_profile_pd = pd.DataFrame(employee_github_from_profile,  columns=["uu_user_id", "github_user_url"])
employee_github_from_cv_pd = pd.DataFrame(employee_github_from_cv,  columns=["uu_user_id", "github_user_url"])

employee_github_from_links_pd = employee_github_from_links_pd.dropna()
employee_github_from_profile_pd = employee_github_from_profile_pd.dropna()
employee_github_from_cv_pd = employee_github_from_cv_pd.dropna()


p = Path("repository_collection", "university_profile_pages","results")
p.mkdir(parents=True, exist_ok=True)

employee_github_from_links_pd.to_csv(Path("repository_collection", "university_profile_pages","results", "employees_github_from_links_urls.csv"), index = False)
employee_github_from_profile_pd.to_csv(Path("repository_collection", "university_profile_pages","results", "employees_github_from_profile_urls.csv"), index = False)
employee_github_from_cv_pd.to_csv(Path("repository_collection", "university_profile_pages","results", "employees_github_from_cv_urls.csv"), index = False)