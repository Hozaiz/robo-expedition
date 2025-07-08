import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_USERNAME = "octocat"

def get_headers():
    """
    Returns GitHub API headers with optional Authorization token from env.
    """
    token = os.getenv("GITHUB_API_KEY", "")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def get_github_profile(username: str = None) -> dict:
    """
    Fetches GitHub profile details and recent repositories.
    """
    username = username or os.getenv("GITHUB_USERNAME", DEFAULT_USERNAME)
    url_profile = f"https://api.github.com/users/{username}"
    url_repos = f"https://api.github.com/users/{username}/repos?per_page=5&sort=updated"

    try:
        user_resp = requests.get(url_profile, headers=get_headers(), timeout=10)
        repos_resp = requests.get(url_repos, headers=get_headers(), timeout=10)

        if user_resp.ok and repos_resp.ok:
            user_data = user_resp.json()
            repos = repos_resp.json()

            return {
                "avatar_url": user_data.get("avatar_url", ""),
                "name": user_data.get("login", "N/A"),
                "bio": user_data.get("bio") or "No bio provided.",
                "repos": [
                    {"name": repo.get("name", ""), "html_url": repo.get("html_url", "#")}
                    for repo in repos
                ],
            }

    except Exception as e:
        print(f"[GitHub Profile Error] {e}")

    return {
        "avatar_url": "",
        "name": "N/A",
        "bio": "GitHub profile fetch failed.",
        "repos": [],
    }


def get_pull_requests(username: str = None) -> list:
    """
    Fetches public pull requests authored by the specified user.
    """
    username = username or os.getenv("GITHUB_USERNAME", DEFAULT_USERNAME)
    url_prs = f"https://api.github.com/search/issues?q=author:{username}+type:pr"

    try:
        prs_resp = requests.get(url_prs, headers=get_headers(), timeout=10)
        if prs_resp.ok:
            items = prs_resp.json().get("items", [])
            return [
                {
                    "title": pr.get("title", "Untitled"),
                    "html_url": pr.get("html_url", "#"),
                    "state": pr.get("state", "unknown"),
                }
                for pr in items
            ]

    except Exception as e:
        print(f"[GitHub PR Fetch Error] {e}")

    return []
