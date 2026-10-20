#!/usr/bin/env python3
"""Permanently delete the imported backlog: every issue carrying a backlog-key
marker, and the "Sprint NN" milestones. Issues without the marker are never touched.

Runs in GitHub Actions (see .github/workflows/reset-backlog.yml). Deleting issues
needs a token from a repository admin (ADMIN_TOKEN); milestones use GITHUB_TOKEN.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API = "https://api.github.com"
REPO = os.environ["GITHUB_REPOSITORY"]
ADMIN_TOKEN = os.environ["ADMIN_TOKEN"]
REPO_TOKEN = os.environ["GITHUB_TOKEN"]
DRY_RUN = os.environ.get("DRY_RUN", "false") == "true"
PAUSE = float(os.environ.get("PAUSE_SECONDS") or 1.5)
MARKER = re.compile(r"<!-- backlog-key: (.+?) -->")
SPRINT = re.compile(r"^Sprint \d+$")


def request(method, url, token, payload=None, attempt=0):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read()
            return json.loads(body) if body else None, resp.headers
    except urllib.error.HTTPError as err:
        text = err.read().decode(errors="replace")
        limited = err.code == 429 or (err.code == 403 and "rate limit" in text.lower())
        if limited and attempt < 8:
            wait = int(err.headers.get("Retry-After") or 0) or min(60 * 2 ** attempt, 900)
            print(f"  rate limited, waiting {wait}s")
            time.sleep(wait)
            return request(method, url, token, payload, attempt + 1)
        if err.code >= 500 and attempt < 4:
            time.sleep(10 * (attempt + 1))
            return request(method, url, token, payload, attempt + 1)
        raise RuntimeError(f"{method} {url} -> {err.code}: {text[:500]}")


def paginate(path, token):
    url, items = f"{API}{path}", []
    while url:
        page, headers = request("GET", url, token)
        items.extend(page)
        nxt = re.search(r'<([^>]+)>; rel="next"', headers.get("Link") or "")
        url = nxt.group(1) if nxt else None
    return items


def main():
    issues = [i for i in paginate(f"/repos/{REPO}/issues?state=all&per_page=100", REPO_TOKEN)
              if "pull_request" not in i and MARKER.search(i.get("body") or "")]
    # Tasks first, then features, then epics, so no parent is deleted before its children.
    issues.sort(key=lambda i: -MARKER.search(i["body"]).group(1).count("/"))
    print(f"{len(issues)} backlog issues to delete")
    deleted = 0
    for issue in issues:
        if DRY_RUN:
            print(f"would delete #{issue['number']} {issue['title']}")
            continue
        res, _ = request("POST", f"{API}/graphql", ADMIN_TOKEN, {
            "query": "mutation($id:ID!){deleteIssue(input:{issueId:$id}){clientMutationId}}",
            "variables": {"id": issue["node_id"]}})
        if res.get("errors"):
            raise RuntimeError(f"deleting #{issue['number']} failed: {res['errors']}")
        deleted += 1
        if deleted % 50 == 0:
            print(f"  {deleted} deleted")
        time.sleep(PAUSE)

    milestones = [m for m in paginate(f"/repos/{REPO}/milestones?state=all&per_page=100", REPO_TOKEN)
                  if SPRINT.match(m["title"])]
    for m in milestones:
        if DRY_RUN:
            print("would delete milestone", m["title"])
            continue
        request("DELETE", f"{API}/repos/{REPO}/milestones/{m['number']}", REPO_TOKEN)

    summary = f"Deleted {deleted} issues and {0 if DRY_RUN else len(milestones)} sprint milestones."
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(summary + "\n")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print("ERROR:", exc)
        sys.exit(1)
