#!/usr/bin/env python3
"""Merge backlog fragments, validate them, schedule tasks into sprints, and
write backlog.json (input for the GitHub importer) and BACKLOG.md (overview)."""
import glob
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SPRINT_CAPACITY = 100  # effort points = hours, including the owner's testing time
TIERS = ["MVP", "Good to have", "Future improvement"]
AREAS = {"backend": "Backend", "ios": "iOS", "android": "Android", "content": "Content",
         "infra": "Infra", "design": "Design", "testing": "Test"}
LABELS = {
    "epic": ("5319e7", "Big area of work (DevOps-style epic)"),
    "MVP": ("0e8a16", "Release tier: needed in the first usable version"),
    "Good to have": ("1d76db", "Release tier: after the MVP, still planned"),
    "Future improvement": ("bfdadc", "Release tier: later, not scheduled"),
    **{f"area:{a}": ("fbca04", f"{n} work") for a, n in AREAS.items()},
}


def fail(msg):
    print("ERROR:", msg)
    sys.exit(1)


def load():
    epics = []
    for path in sorted(glob.glob(os.path.join(HERE, "[a-z]-*.json"))):
        with open(path) as f:
            epics.extend(json.load(f))
    epics.sort(key=lambda e: e["key"])
    return epics


def validate(epics):
    rows = {r["id"]: r for r in json.load(open(os.path.join(HERE, "priorities-final.json")))}
    seen = Counter()
    for e in epics:
        for f in e["features"]:
            seen[f["key"]] += 1
            if f["priority"] not in TIERS:
                fail(f"{f['key']}: bad priority {f['priority']}")
            if f["key"] in rows and rows[f["key"]]["priority"] != f["priority"]:
                fail(f"{f['key']}: priority {f['priority']} != {rows[f['key']]['priority']}")
            if f["priority"] == "Future improvement" and f["tasks"]:
                fail(f"{f['key']}: future feature has tasks")
            if f["priority"] != "Future improvement" and not f["tasks"]:
                fail(f"{f['key']}: no tasks")
            for t in f["tasks"]:
                if t["area"] not in AREAS:
                    fail(f"{f['key']}: bad area {t['area']}")
                if not (isinstance(t["hours"], int) and 1 <= t["hours"] <= 8):
                    fail(f"{f['key']}: bad hours {t['hours']} in '{t['title']}'")
    missing = [k for k in rows if k not in seen]
    dupes = [k for k, n in seen.items() if n > 1]
    if missing:
        fail(f"missing rows: {missing}")
    if dupes:
        fail(f"duplicate feature keys: {dupes}")


def schedule(epics):
    """Order tasks by (tier, seq, epic, feature, task) and fill 100-hour sprints.
    A new sprint always starts at the MVP / Good to have boundary."""
    queue = []
    for ei, e in enumerate(epics):
        for fi, f in enumerate(e["features"]):
            for ti, t in enumerate(f["tasks"]):
                queue.append((TIERS.index(f["priority"]), f["seq"], ei, fi, ti, e, f, t))
    queue.sort(key=lambda q: q[:5])
    sprints, current, tier = [], None, None
    for tier_i, _, _, _, _, e, f, t in queue:
        if current is None or tier_i != tier or current["hours"] + t["hours"] > SPRINT_CAPACITY:
            current = {"number": len(sprints) + 1, "tier": TIERS[tier_i], "hours": 0, "epics": Counter()}
            sprints.append(current)
            tier = tier_i
        current["hours"] += t["hours"]
        current["epics"][e["title"]] += t["hours"]
        t["sprint"] = current["number"]
    for s in sprints:
        s["title"] = f"Sprint {s['number']:02d}"
    return sprints


def dependency_title(dep, titles):
    """Resolve a feature key, or a loose "E00:<name>" reference to a Foundations feature."""
    if dep in titles:
        return titles[dep]
    name = dep.split(":", 1)[-1].strip().lower()
    words = [w for w in name.replace("-", " ").split() if len(w) > 2]
    best = max(titles.items(), key=lambda kv: sum(w.rstrip("s") in kv[1].lower() for w in words))
    if words and sum(w.rstrip("s") in best[1].lower() for w in words) >= max(1, len(words) - 1):
        return best[1]
    return f"Foundations: {dep.split(':', 1)[-1].strip()}" if dep.startswith("E00:") else dep


def marker(key):
    return f"\n\n<!-- backlog-key: {key} -->"


def render(epics, sprints):
    titles = {f["key"]: f["title"] for e in epics for f in e["features"]}
    sprint_title = {s["number"]: s["title"] for s in sprints}
    issues = []
    for e in epics:
        tiers = Counter(f["priority"] for f in e["features"])
        hours = sum(t["hours"] for f in e["features"] for t in f["tasks"])
        body = (f"{e['summary']}\n\n**Plan:** {e['plan_ref']}\n\n"
                f"**Features:** " + ", ".join(f"{n} {t}" for t, n in tiers.items()) +
                f"\n**Estimated effort:** {hours} h (scheduled features)" + marker(e["key"]))
        issues.append({"key": e["key"], "kind": "epic", "title": f"Epic: {e['title']}",
                       "type": "Feature", "labels": ["epic"], "body": body, "parent": None, "milestone": None})
        for f in e["features"]:
            hours = sum(t["hours"] for t in f["tasks"])
            spr = sorted({t["sprint"] for t in f["tasks"]})
            deps = [dependency_title(d, titles) for d in f.get("depends_on", [])]
            lines = [f"**User story:** {f['story']}", "", "**Acceptance criteria**"]
            lines += [f"- [ ] {a}" for a in f["acceptance"]]
            lines += ["", f"**Release tier:** {f['priority']}"]
            if f["tasks"]:
                lines.append(f"**Estimated effort:** {hours} h across {len(f['tasks'])} tasks (includes testing)")
                lines.append("**Sprints:** " + ", ".join(sprint_title[s] for s in spr))
            else:
                lines.append("**Not scheduled.** Tasks will be broken down when this is planned.")
            if deps:
                lines.append("**Depends on:** " + "; ".join(deps))
            lines.append(f"**Plan:** {e['plan_ref']} · row {f['key']}")
            issues.append({"key": f"{e['key']}/{f['key']}", "kind": "feature", "title": f["title"],
                           "type": "Feature", "labels": [f["priority"]], "body": "\n".join(lines) + marker(f"{e['key']}/{f['key']}"),
                           "parent": e["key"], "milestone": None})
            for ti, t in enumerate(f["tasks"], 1):
                key = f"{e['key']}/{f['key']}/T{ti}"
                body = (f"{t['description']}\n\n**Estimate:** {t['hours']} h (includes testing)\n"
                        f"**Area:** {AREAS[t['area']]}\n**Sprint:** {sprint_title[t['sprint']]}\n"
                        f"**Feature:** {f['title']} ({f['priority']})" + marker(key))
                issues.append({"key": key, "kind": "task", "title": f"[{AREAS[t['area']]}] {t['title']}",
                               "type": "Task", "labels": [f["priority"], f"area:{t['area']}"], "body": body,
                               "parent": f"{e['key']}/{f['key']}", "milestone": sprint_title[t["sprint"]]})
    milestones = [{"title": s["title"],
                   "description": f"Release tier: {s['tier']} · Capacity {SPRINT_CAPACITY} h · Planned {s['hours']} h · "
                                  + ", ".join(f"{k} {v} h" for k, v in s["epics"].most_common())}
                  for s in sprints]
    labels = [{"name": n, "color": c, "description": d} for n, (c, d) in LABELS.items()]
    return {"labels": labels, "milestones": milestones, "issues": issues}


def overview(epics, sprints, data):
    kinds = Counter(i["kind"] for i in data["issues"])
    lines = ["# Backlog overview", "",
             "Generated by `planning/backlog/build.py` from the fragments in `planning/backlog/`. "
             f"Effort is in hours (including the owner's testing time). Sprint capacity: {SPRINT_CAPACITY} h.", "",
             f"**Issues:** {kinds['epic']} epics, {kinds['feature']} features, {kinds['task']} tasks", ""]
    by_tier = defaultdict(int)
    for s in sprints:
        by_tier[s["tier"]] += s["hours"]
    for tier in TIERS[:2]:
        n = sum(1 for s in sprints if s["tier"] == tier)
        lines.append(f"- **{tier}:** {by_tier[tier]} h in {n} sprints")
    lines += ["", "## Sprints", "", "| Sprint | Tier | Planned | Main epics |", "|---|---|---|---|"]
    for s in sprints:
        main = ", ".join(f"{k} ({v} h)" for k, v in s["epics"].most_common(3))
        lines.append(f"| {s['title']} | {s['tier']} | {s['hours']} h | {main} |")
    lines += ["", "## Epics", "", "| Epic | MVP | Good to have | Future | Hours |", "|---|---|---|---|---|"]
    for e in epics:
        c = Counter(f["priority"] for f in e["features"])
        h = sum(t["hours"] for f in e["features"] for t in f["tasks"])
        lines.append(f"| {e['key']} {e['title']} | {c['MVP']} | {c['Good to have']} | {c['Future improvement']} | {h} |")
    return "\n".join(lines) + "\n"


def main():
    epics = load()
    validate(epics)
    sprints = schedule(epics)
    data = render(epics, sprints)
    with open(os.path.join(HERE, "backlog.json"), "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, "BACKLOG.md"), "w") as f:
        f.write(overview(epics, sprints, data))
    print(f"{len(data['issues'])} issues, {len(sprints)} sprints")


if __name__ == "__main__":
    main()
