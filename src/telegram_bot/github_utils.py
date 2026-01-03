import json 
import os
import base64
import requests

from telegram_main import GITHUB_TOKEN


REPO = 'pilaarfdeez/Seguidor_vuelos'
BRANCH = 'main'
API = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


def get_file(path: str) -> dict:
    url = f"{API}/repos/{REPO}/contents/{path}"
    r = requests.get(url, headers=HEADERS, params={"ref": BRANCH})
    r.raise_for_status()
    return r.json()


def update_json_file(path: str, update_fn, commit_message: str):
    file = get_file(path)

    content = base64.b64decode(file["content"]).decode()
    data = json.loads(content)

    # user-defined mutation
    update_fn(data)

    new_content = json.dumps(data, indent=4)
    print(new_content)
    encoded = base64.b64encode(new_content.encode()).decode()

    payload = {
        "message": commit_message,
        "content": encoded,
        "sha": file["sha"],
        "branch": BRANCH,
    }

    url = f"{API}/repos/{REPO}/contents/{path}"
    r = requests.put(url, headers=HEADERS, json=payload)
    r.raise_for_status()
