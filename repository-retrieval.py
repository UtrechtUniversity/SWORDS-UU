from ghapi.all import GhApi
api = GhApi()
topic_repos = api.search.repos("topic:utrecht-university")



for key, value in topic_repos.items():
    print("Key: %s | Value: %s " % (key, value))