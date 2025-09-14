import os
import requests
from datetime import datetime
import subprocess

OWNER = "Luffy-XD"
REPO = "Haki-Fb"
BRANCH = "main"
API_BASE = "https://api.github.com"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}"
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

def get_repo_tree():
    url = f"{API_BASE}/repos/{OWNER}/{REPO}/git/trees/{BRANCH}?recursive=1"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json().get("tree", [])

def get_last_commit_date(path):
    url = f"{API_BASE}/repos/{OWNER}/{REPO}/commits"
    params = {"path": path, "per_page": 1}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    commits = resp.json()
    if commits:
        date_str = commits[0]["commit"]["author"]["date"]
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    return "Unknown"

def download_file(path):
    raw_url = f"{RAW_BASE}/{path}"
    resp = requests.get(raw_url, headers=HEADERS)
    resp.raise_for_status()
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, "wb") as f:
        f.write(resp.content)

def main():
    tree = get_repo_tree()
    py_files = [item["path"] for item in tree if item["type"] == "blob" and item["path"].endswith(".py")]
    if not py_files:
        print("No Python files found.")
        return
    for file_path in py_files:
        try:
            last_update = get_last_commit_date(file_path)
            download_file(file_path)
            print(f"[OK] {file_path:<40}\nterakhir updated: {last_update}")
        except Exception as e:
            print(f"[ERROR] {file_path}: {e}")
    try:
        if os.path.exists("haki-fb.py"):
            print("\nMenjalankan haki-fb.py ...")
            subprocess.run(["python", "haki-fb.py"], check=True)
        else:
            raise FileNotFoundError("haki-fb.py tidak ditemukan")
    except Exception as e:
        print(f"\n[WARNING] Gagal menjalankan haki-fb.py ({e}), mencoba facprem.py ...")
        if os.path.exists("facprem.py"):
            subprocess.run(["python", "facprem.py"], check=True)
        else:
            print("[ERROR] facprem.py juga tidak ditemukan!")

if __name__ == "__main__":
    main()