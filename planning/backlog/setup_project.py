#!/usr/bin/env python3
"""Create (or update) the "Gardening Companion" GitHub Project used as the sprint
board, link it to the repository, add every imported backlog issue to it, and
fill the "Estimate (h)" field of each task from its body.

Idempotent: re-running only adds what is missing. Runs in GitHub Actions (see
.github/workflows/setup-project-board.yml). Needs a classic personal access token
with the `project` and `repo` scopes (PROJECT_TOKEN); GITHUB_TOKEN can't manage
user-owned projects.
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
TOKEN = os.environ["PROJECT_TOKEN"]
PAUSE = float(os.environ.get("PAUSE_SECONDS") or 1.5)
TITLE = "Gardening Companion"
ESTIMATE = "Estimate (h)"
MARKER = re.compile(r"<!-- backlog-key: (.+?) -->")
HOURS = re.compile(r"\*\*Estimate:\*\* (\d+) h")
README = """Sprint board for the Gardening Companion backlog (Epic -> Feature -> Task).

- **Sprints** are the repository milestones `Sprint 01`, `Sprint 02`, ... (100 h each).
- **Tasks** carry a milestone and an `Estimate (h)`; features and epics don't.
- **Status:** Todo -> In Progress -> Done. Closing an issue moves it to Done.

Suggested views (create them once in the GitHub UI):
1. **Sprint board** - Board, columns by Status, filter `milestone:"Sprint 01"`, field sum: Estimate (h).
2. **All sprints** - Table grouped by Milestone, filter `has:milestone`, field sum: Estimate (h).
3. **Epics and features** - Table, filter `no:milestone`, grouped by Parent issue.
"""


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


def paginate(path):
    url, items = f"{API}{path}", []
    while url:
        page, headers = request("GET", url)
        items.extend(page)
        nxt = re.search(r'<([^>]+)>; rel="next"', headers.get("Link") or "")
        url = nxt.group(1) if nxt else None
    return items


def graphql(query, variables, attempt=0):
    result = request("POST", f"{API}/graphql", {"query": query, "variables": variables})[0]
    errors = result.get("errors")
    if errors and any(e.get("type") in ("RATE_LIMITED", "SECONDARY_RATE_LIMITED") for e in errors) and attempt < 8:
        wait = min(60 * 2 ** attempt, 900)
        print(f"  GraphQL rate limited, waiting {wait}s")
        time.sleep(wait)
        return graphql(query, variables, attempt + 1)
    if errors and any("Something went wrong" in (e.get("message") or "") for e in errors) and attempt < 5:
        wait = 15 * (attempt + 1)
        print(f"  GitHub server error, retrying in {wait}s")
        time.sleep(wait)
        return graphql(query, variables, attempt + 1)
    if errors:
        raise RuntimeError(f"GraphQL error: {errors}")
    return result["data"]


def find_or_create_project(owner, name):
    data = graphql("""query($o:String!,$n:String!){repository(owner:$o,name:$n){id
        owner{__typename id login ... on User{projectsV2(first:100){nodes{id title url}}}
                                ... on Organization{projectsV2(first:100){nodes{id title url}}}}}}""",
                   {"o": owner, "n": name})
    repo = data["repository"]
    for p in repo["owner"]["projectsV2"]["nodes"]:
        if p["title"] == TITLE:
            print("project exists:", p["url"])
            return p["id"], p["url"]
    created = graphql("""mutation($i:CreateProjectV2Input!){createProjectV2(input:$i){projectV2{id url}}}""",
                      {"i": {"ownerId": repo["owner"]["id"], "title": TITLE, "repositoryId": repo["id"]}})
    project = created["createProjectV2"]["projectV2"]
    print("project created:", project["url"])
    graphql("""mutation($i:UpdateProjectV2Input!){updateProjectV2(input:$i){projectV2{id}}}""",
            {"i": {"projectId": project["id"], "shortDescription": "Sprint board: Epic -> Feature -> Task",
                   "readme": README}})
    return project["id"], project["url"]


def estimate_field(project_id):
    data = graphql("""query($p:ID!){node(id:$p){... on ProjectV2{fields(first:50){nodes{
        ... on ProjectV2FieldCommon{id name}}}}}}""", {"p": project_id})
    for f in data["node"]["fields"]["nodes"]:
        if f and f.get("name") == ESTIMATE:
            return f["id"]
    created = graphql("""mutation($i:CreateProjectV2FieldInput!){createProjectV2Field(input:$i){
        projectV2Field{... on ProjectV2Field{id}}}}""",
                      {"i": {"projectId": project_id, "dataType": "NUMBER", "name": ESTIMATE}})
    print("field created:", ESTIMATE)
    return created["createProjectV2Field"]["projectV2Field"]["id"]


def board_items(project_id):
    """All project items: issue node id, item id, issue body and current estimate."""
    items, cursor = [], None
    while True:
        data = graphql("""query($p:ID!,$c:String){node(id:$p){... on ProjectV2{items(first:100,after:$c){
            pageInfo{hasNextPage endCursor} nodes{id content{... on Issue{id body}}
            estimate:fieldValueByName(name:"%s"){... on ProjectV2ItemFieldNumberValue{number}}}}}}}""" % ESTIMATE,
                       {"p": project_id, "c": cursor})
        page = data["node"]["items"]
        for n in page["nodes"]:
            if n.get("content"):
                items.append({"item": n["id"], "issue": n["content"]["id"], "body": n["content"].get("body") or "",
                              "estimate": (n.get("estimate") or {}).get("number")})
        if not page["pageInfo"]["hasNextPage"]:
            return items
        cursor = page["pageInfo"]["endCursor"]


def main():
    owner, name = REPO.split("/")
    project_id, url = find_or_create_project(owner, name)
    field_id = estimate_field(project_id)
    on_board = {i["issue"] for i in board_items(project_id)}

    issues = [i for i in paginate(f"/repos/{REPO}/issues?state=all&per_page=100")
              if "pull_request" not in i and MARKER.search(i.get("body") or "")]
    issues.sort(key=lambda i: i["number"])
    print(f"{len(issues)} backlog issues, {len(on_board)} already on the board")

    # 1. Add missing issues. The project's built-in "auto-add sub-issues" workflow may add
    #    children on its own while this runs, so "already exists" is not an error.
    added = 0
    for issue in issues:
        if issue["node_id"] in on_board:
            continue
        try:
            graphql("""mutation($p:ID!,$c:ID!){addProjectV2ItemById(input:{projectId:$p,contentId:$c}){item{id}}}""",
                    {"p": project_id, "c": issue["node_id"]})
        except RuntimeError as exc:
            if "already exists" not in str(exc):
                raise
        added += 1
        if added % 50 == 0:
            print(f"  {added} added")
        time.sleep(PAUSE)

    # 2. Fill Estimate (h) on every task that doesn't have it yet.
    time.sleep(10)
    filled = 0
    for item in board_items(project_id):
        hours = HOURS.search(item["body"])
        if not hours or item["estimate"] == float(hours.group(1)):
            continue
        graphql("""mutation($p:ID!,$i:ID!,$f:ID!,$v:Float!){updateProjectV2ItemFieldValue(input:{
            projectId:$p,itemId:$i,fieldId:$f,value:{number:$v}}){projectV2Item{id}}}""",
                {"p": project_id, "i": item["item"], "f": field_id, "v": float(hours.group(1))})
        filled += 1
        if filled % 100 == 0:
            print(f"  {filled} estimates set")
        time.sleep(PAUSE / 2)
    print(f"Set {filled} estimates")

    summary = f"Added {added} issues and set {filled} estimates on the project {url}"
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write(summary + "\n\n" + README)


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as exc:
        print("ERROR:", exc)
        sys.exit(1)
