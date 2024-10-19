import requests

def get_repo_commits(repo, token):
    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return []
