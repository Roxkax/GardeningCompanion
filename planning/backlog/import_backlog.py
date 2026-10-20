#!/usr/bin/env python3
"""Create labels, sprint milestones and the Epic -> Feature -> Task issue tree
from backlog.json. Idempotent: issues already carrying a backlog-key marker are
skipped, so the import can be re-run to resume after a failure.

Runs in GitHub Actions with GITHUB_TOKEN (see .github/workflows/import-backlog.yml).
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
TOKEN = os.environ["GITHUB_TOKEN"]
LIMIT = int(os.environ.get("LIMIT") or 0)
DRY_RUN = os.environ.get("DRY_RUN", "false") == "true"
PAUSE = float(os.environ.get("PAUSE_SECONDS") or 4)
MARKER = re.compile(r"<!-- backlog-key: (.+?) -->")


def request(method, url, payload=None, attempt=0):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {TOKEN}",
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
            return request(method, url, payload, attempt + 1)
        if err.code >= 500 and attempt < 4:
            time.sleep(10 * (attempt + 1))
            return request(method, url, payload, attempt + 1)
        raise RuntimeError(f"{method} {url} -> {err.code}: {text[:500]}")


def rest(method, path, payload=None):
    return request(method, f"{API}{path}", payload)[0]


def paginate(path):
    url, items = f"{API}{path}", []
    while url:
        page, headers = request("GET", url)
        items.extend(page)
        nxt = re.search(r'<([^>]+)>; rel="next"', headers.get("Link") or "")
        url = nxt.group(1) if nxt else None
    return items


def graphql(query, variables, attempt=0):
    result = rest("POST", "/graphql", {"query": query, "variables": variables})
    errors = result.get("errors")
    if errors and any(e.get("type") in ("RATE_LIMITED", "SECONDARY_RATE_LIMITED") for e in errors) and attempt < 8:
        wait = min(60 * 2 ** attempt, 900)
        print(f"  GraphQL rate limited, waiting {wait}s")
        time.sleep(wait)
        return graphql(query, variables, attempt + 1)
    return result


def main():
    backlog = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "backlog.json")))
    owner, name = REPO.split("/")

    # Labels
    existing = {l["name"] for l in paginate(f"/repos/{REPO}/labels?per_page=100")}
    for label in backlog["labels"]:
        if label["name"] not in existing and not DRY_RUN:
            rest("POST", f"/repos/{REPO}/labels", label)
            print("label created:", label["name"])

    # Sprint milestones
    milestones = {m["title"]: m for m in paginate(f"/repos/{REPO}/milestones?state=all&per_page=100")}
    for m in backlog["milestones"]:
        if m["title"] not in milestones and not DRY_RUN:
            milestones[m["title"]] = rest("POST", f"/repos/{REPO}/milestones", m)
            print("milestone created:", m["title"])

    # Node IDs for GraphQL
    meta = graphql("""query($o:String!,$n:String!){repository(owner:$o,name:$n){id
        issueTypes(first:25){nodes{id name}} labels(first:100){nodes{id name}}}}""", {"o": owner, "n": name})
    repo = meta["data"]["repository"]
    types = {t["name"]: t["id"] for t in (repo.get("issueTypes") or {}).get("nodes", [])}
    label_ids = {l["name"]: l["id"] for l in repo["labels"]["nodes"]}

    # Issues already imported
    done = {}
    for issue in paginate(f"/repos/{REPO}/issues?state=all&per_page=100"):
        m = MARKER.search(issue.get("body") or "")
        if m:
            done[m.group(1)] = {"number": issue["number"], "id": issue["id"], "node_id": issue["node_id"]}
    print(f"{len(done)} backlog issues already exist; {len(backlog['issues'])} in backlog.json")

    use_parent_field = True
    created = 0
    for item in backlog["issues"]:
        if item["key"] in done:
            continue
        if LIMIT and created >= LIMIT:
            break
        parent = done.get(item["parent"]) if item["parent"] else None
        if item["parent"] and not parent:
            raise RuntimeError(f"parent {item['parent']} of {item['key']} not created")
        if DRY_RUN:
            print("would create:", item["title"])
            created += 1
            continue
        inp = {"repositoryId": repo["id"], "title": item["title"], "body": item["body"],
               "labelIds": [label_ids[l] for l in item["labels"]]}
        if item["type"] in types:
            inp["issueTypeId"] = types[item["type"]]
        if item["milestone"]:
            inp["milestoneId"] = milestones[item["milestone"]]["node_id"]
        if parent and use_parent_field:
            inp["parentIssueId"] = parent["node_id"]
        mutation = "mutation($i:CreateIssueInput!){createIssue(input:$i){issue{number databaseId id}}}"
        res = graphql(mutation, {"i": inp})
        if res.get("errors") and "parentIssueId" in json.dumps(res["errors"]):
            print("  parentIssueId not supported; falling back to the sub-issues REST API")
            use_parent_field = False
            inp.pop("parentIssueId", None)
            res = graphql(mutation, {"i": inp})
        if res.get("errors"):
            raise RuntimeError(f"createIssue failed for {item['key']}: {res['errors']}")
        issue = res["data"]["createIssue"]["issue"]
        done[item["key"]] = {"number": issue["number"], "id": issue["databaseId"], "node_id": issue["id"]}
        if parent and not use_parent_field:
            time.sleep(PAUSE / 2)
            rest("POST", f"/repos/{REPO}/issues/{parent['number']}/sub_issues", {"sub_issue_id": issue["databaseId"]})
        created += 1
        print(f"#{issue['number']} {item['title']}")
        time.sleep(PAUSE)

    remaining = sum(1 for i in backlog["issues"] if i["key"] not in done)
    summary = f"Created {created} issues. {remaining} still to create."
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
