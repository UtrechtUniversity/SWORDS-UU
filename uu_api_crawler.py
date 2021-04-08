import pandas as pd
import json
import requests
import time

def get_employees_url(faculty_number):
    url = f"https://www.uu.nl/medewerkers/RestApi/Public/GetEmployeesOrganogram?f={faculty_number}&l=EN&fullresult=true"
    json_nested  = requests.get(url)
    df = pd.DataFrame(json_nested.json()["Employees"])
    return df["Url"]

#print(get_employees_url(3))


def get_employee_links(url):
    time.sleep(1)#avoid ban by adding time between requests
    API_link = requests.get(f"https://www.uu.nl/medewerkers/RestApi/Public/getEmployeeData?page={url}")
    API_json = API_link.json()

    try:#try if a key exists for links of the employee
        return  API_json["Employee"]['Links']
    except:
        return "no links in user API"
def get_employee_specific_link(url, search_query):
    time.sleep(1)#avoid ban by adding time between requests
    API_link = requests.get(f"https://www.uu.nl/medewerkers/RestApi/Public/getEmployeeData?page={url}")
    API_json = API_link.json()

    try:#try if a key exists for links of the employee
        employee_link_list =  API_json["Employee"]['Links']
        for link in employee_link_list:
            if  search_query in link['Url']:
                return item['Url']
        return "query not found in links"
    except:
        return "no links in user API"

def get_employee_github(url):
    time.sleep(1)#avoid ban by adding time between requests
    API_link = requests.get(f"https://www.uu.nl/medewerkers/RestApi/Public/getEmployeeData?page={url}")
    API_json = API_link.json()

    try:#try if a key exists for links of the employee
        employee_link_list =  API_json["Employee"]['Links']
        for link in employee_link_list:
            if "github" in link['Url']:
                return link['Url']
        return "no github page in user links"
    except:
        return "no links in user API"
def get_employee_profile_mention(url, query):
    query = query.lower() # Casing doesn't matter for search
    time.sleep(1)#avoid ban by adding time between requests
    API_link = requests.get(f"https://www.uu.nl/medewerkers/RestApi/Public/getEmployeeData?page={url}")
    API_json = API_link.json()

    try:#try if a key exists for profile of the employee
        employee_profile =  API_json["Employee"]['Profile']
        if query in employee_profile.lower():
            return f"{query} found in user profile"
        return "query not found in user in user profile"
    except:
        return "no profile description in user API"

employee_links = []
employee_github = []
employee_link_query_test = []
employee__profile_query_test = []
urls_for_test = list(get_employees_url(3).head())
urls_for_test.append("jdebruin1")  #contains many of these features, so a good example for testing
for url in urls_for_test:
    employee_links.append([url, get_employee_links(url)])
    employee_github.append([url, get_employee_github(url)])
    employee_link_query_test.append([url, get_employee_specific_link(url, "orcid")])
    employee__profile_query_test.append([url, get_employee_profile_mention(url, "open science")])




print(employee_links)
print(employee_github)
print(employee_link_query_test)
print(employee__profile_query_test)
