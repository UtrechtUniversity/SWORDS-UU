from ghapi.all import GhApi, pages
from fastcore.foundation import L

def get_repos(api, user_id):
    """retrieves complete repositories (exluding forked ones) from a specified user_id

    Args:
        api (GhApi object): standard Api object from GhApi
        user_id (string): user id which is named as "login" from the GitHub Api

    Returns:
        L: fastcore list of repositories
    """
    # do first request to store last page variable in api object
    api.search.repos("user:" + user_id, per_page = 100)
    if(api.last_page() > 0):
        query_result = pages(api.search.repos, api.last_page(), "user:" + user_id)
    else:
        # if there is only one page, last_page() will return 0. This will return nothing, so we need to use 1
        query_result = pages(api.search.repos, 1, "user:" + user_id)
    result = L()
    for page in query_result:
        result.extend(page["items"])
    return result

def get_full_name_from_repos(repos):
    """Goes through a list of repos and returns their url

    Args:
        repos (L): fastcore foundation list of repositories

    Returns:
        L: fastcore founation list of full names
    """
    result = L()
    for repo in repos:
        result.append(repo["full_name"])
    return result

def is_student(user_id):
    """Checks whether a GitHub user is a student. The bio of a user is parsed. 
    If it contains phd the user will not be marked as a student. 
    If the bio contains only the word student the user will be marked as a student. If

    Args:
        user_id (string): user id which is named as "login" from the GitHub Api 

    Returns:
        Boolean: Whether the user is a student or not
    """
    user_data = api.users.get_by_username(user_id)
    user_bio = user_data["bio"]
    if (user_bio is not None):
        user_bio = user_bio.lower()
        # PhD students should be included
        mention_phd = "phd" in user_bio
        mention_student = "student" in user_bio
        return (not mention_phd and mention_student)
    else:
        # we can't be sure and therefore keep the user
        return False

if __name__ == '__main__':  
    # example
    user_id = "beld78"
    api = GhApi()
    
    print("Is beld78 a student? " + str(is_student("beld78")))
    repos = get_repos(api, user_id)
    repos_names = get_full_name_from_repos(repos)
    print(repos_names)