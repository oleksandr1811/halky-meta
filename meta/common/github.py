import os
from typing import List, Optional

import requests

from ..model.github import GitHubReleaseEntry, GitHubReleaseIndex


def fetch_releases(api_url: str, sess: requests.Session) -> List[GitHubReleaseEntry]:
    entries: List[GitHubReleaseEntry] = []
    url = api_url
    params = {"per_page": 100}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    while url:
        r = sess.get(url, params=params, headers=headers)
        r.raise_for_status()

        entries += GitHubReleaseIndex.parse_obj(r.json()).__root__

        url = r.links.get("next", {}).get("url")
        params = None

    return entries
