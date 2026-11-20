"""
Pushes local repository to GitHub 'trading-office' using the provided PAT.
Masks credentials in logs and outputs.
"""
import os
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

WORKSPACE = Path('/opt/data/profiles/trading-office-manager/workspace/multi-asset-e2e')

# Read token from secure temporary location or parameter
TOKEN = os.environ.get("GITHUB_TOKEN", "REDACTED")

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(WORKSPACE))
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def sync_github():
    print("=== GITHUB SYNC & PUSH ===")
    
    # 1. Identify GitHub user
    req = urllib.request.Request(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "Hermes-Trading-Office",
            "Accept": "application/vnd.github+json"
        }
    )
    
    try:
        with urllib.request.urlopen(req) as resp:
            user_data = json.loads(resp.read().decode('utf-8'))
            username = user_data.get("login")
            print(f"Authenticated as GitHub user: {username}")
    except Exception as e:
        print(f"Failed to authenticate with GitHub API: {e}")
        return

    # 2. Check if repo trading-office exists, or create it
    repo_name = "trading-office"
    repo_url = f"https://api.github.com/repos/{username}/{repo_name}"
    check_req = urllib.request.Request(
        repo_url,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "User-Agent": "Hermes-Trading-Office",
            "Accept": "application/vnd.github+json"
        }
    )
    
    repo_exists = False
    try:
        with urllib.request.urlopen(check_req) as resp:
            if resp.status == 200:
                repo_exists = True
                print(f"Repository {username}/{repo_name} already exists.")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Repository {username}/{repo_name} does not exist. Creating it...")
            create_req = urllib.request.Request(
                "https://api.github.com/user/repos",
                data=json.dumps({
                    "name": repo_name,
                    "description": "Hermes Trading Office Multi-Asset Workspace & Monitoring Suite",
                    "private": True
                }).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {TOKEN}",
                    "User-Agent": "Hermes-Trading-Office",
                    "Accept": "application/vnd.github+json",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(create_req) as create_resp:
                print(f"Repository created successfully (status {create_resp.status}).")
                repo_exists = True
        else:
            print(f"Error checking repo: {e}")
            return
    except Exception as e:
        print(f"Unexpected error: {e}")
        return

    # 3. Configure Git Remote
    remote_url = f"https://{username}:{TOKEN}@github.com/{username}/{repo_name}.git"
    
    # Remove existing origin if any
    run_cmd("git remote remove origin")
    
    out_rem, err_rem, code_rem = run_cmd(f"git remote add origin {remote_url}")
    print(f"Remote added: code {code_rem}")
    
    # 4. Push to remote
    out_push, err_push, code_push = run_cmd("git push -u origin main --force")
    
    # Mask token in outputs
TOKEN = os.environ.get("GITHUB_TOKEN", "")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
    
    print(f"Git push result (code {code_push}):")
    if sanitized_out:
        print("STDOUT:", sanitized_out)
    if sanitized_err:
        print("STDERR:", sanitized_err)
        
    if code_push == 0:
        print(f"SUCCESS: Project successfully pushed to https://github.com/{username}/{repo_name}")
    else:
        print("Push failed. Inspect errors above.")

if __name__ == '__main__':
    sync_github()
