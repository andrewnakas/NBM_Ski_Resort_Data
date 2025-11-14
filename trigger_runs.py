#!/usr/bin/env python3
"""
Trigger 24 workflow runs to quickly download all NBM GRIB files.
Uses GitHub API to trigger workflow_dispatch events.
"""

import requests
import time
import sys

# Configuration
REPO_OWNER = "andrewnakas"
REPO_NAME = "NBM_Ski_Resort_Data"
WORKFLOW_FILE = "deploy.yml"
BRANCH = "claude/make-github-016QS7Krep1mLSPp2tDqoFM6"
NUM_RUNS = 24

# GitHub API endpoint
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/dispatches"

def trigger_workflow(github_token):
    """Trigger a single workflow run."""
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {github_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    data = {
        "ref": BRANCH
    }

    response = requests.post(API_URL, headers=headers, json=data)
    return response.status_code == 204

def main():
    print("=" * 70)
    print(f"NBM Workflow Trigger Script")
    print(f"Triggering {NUM_RUNS} workflow runs")
    print("=" * 70)

    # Check if token is provided
    if len(sys.argv) < 2:
        print("\n⚠ GitHub token required!")
        print("\nUsage:")
        print("  python trigger_runs.py <GITHUB_TOKEN>")
        print("\nGet a token at: https://github.com/settings/tokens")
        print("Required scope: workflow")
        sys.exit(1)

    github_token = sys.argv[1]

    success_count = 0
    fail_count = 0

    for i in range(1, NUM_RUNS + 1):
        print(f"\nTriggering run {i}/{NUM_RUNS}...", end=" ")

        if trigger_workflow(github_token):
            print("✓")
            success_count += 1
        else:
            print("✗")
            fail_count += 1

        # Small delay to avoid rate limiting
        time.sleep(0.5)

    print("\n" + "=" * 70)
    print(f"✓ Triggered {success_count}/{NUM_RUNS} workflow runs")
    if fail_count > 0:
        print(f"✗ Failed: {fail_count}")
    print("=" * 70)

    print(f"\nMonitor progress at:")
    print(f"https://github.com/{REPO_OWNER}/{REPO_NAME}/actions")

    print(f"\nYour site will update with each completed run:")
    print(f"https://{REPO_OWNER.lower()}.github.io/{REPO_NAME}/")

    print(f"\nExpected completion time: ~90 minutes")
    print(f"(24 runs × ~3.5 min per run, running sequentially)")

if __name__ == "__main__":
    main()
