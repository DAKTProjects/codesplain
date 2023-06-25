from ast import List
import os

from dotenv import load_dotenv
from github import Github, Auth
import requests

load_dotenv()

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    print("Make sure to add an entry in the .env file called GITHUB_TOKEN. You can get a token from GitHub > Settings > Developer Settings > Personal Access Tokens.")
    exit(1)

auth = Auth.Token(os.environ.get('GITHUB_TOKEN'))
g = Github(auth=auth)


def get_prs(repo: str) -> List[dict]:
    git_repo = g.get_repo(repo)
    closed_prs = git_repo.get_pulls('closed')
    pr_embeds = []
    for pr in closed_prs:
        if pr.is_merged:
            response = requests.get(pr.patch_url)
            if response.ok:
                pr_embeds.append({
                    'title': pr.title,
                    'body': pr.body,
                    'diff': response.text
                })
    return pr_embeds


if __name__ == '__main__':
    get_prs('evanw/kiwi')
