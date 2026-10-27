# GitHub setup: work tracking, backlog as code and CI/CD

This is the GitHub configuration agreed for **Gardening Companion**, written so it can be reused in another project. It covers:

- how the work is tracked (Azure DevOps style, on GitHub)
- how the backlog is kept as code and imported
- the sprint board
- branches, pull requests and commit identity
- the continuous integration checks
- QA and prod deployments of the API.

The scripts and workflows referenced here live in this repository and can be copied as they are; only names and paths change.

---

## 1. Work tracking: Epic → Feature → Task

| DevOps idea | On GitHub |
|---|---|
| Epic | An issue of type **Feature** with the **`epic`** label (use an Epic issue type if your account has one) |
| PBI / Feature | An issue of type **Feature**, a **sub-issue** of its epic, with a user story and acceptance criteria |
| Task | An issue of type **Task**, a **sub-issue** of its feature, with an hour estimate in its body |
| Sprint | A **milestone** named `Sprint 01`, `Sprint 02`, … |
| Tags | **Labels**: release tier (`MVP`, `Good to have`, `Future improvement`), `epic`, and area (`area:backend`, `area:ios`, `area:android`, `area:content`, `area:infra`, `area:design`, `area:testing`) |

- **Sprints have a fixed capacity:** 100 effort points, where **1 point = 1 hour, including the owner's testing time.**
- **Only tasks get a sprint.** Features and epics have no milestone; their progress comes from their sub-issues.
- **Future-improvement features have no tasks** until they are scheduled.

## 2. Backlog as code

The backlog is **not edited by hand on GitHub**. Its source of truth is JSON in the repository, so it can be reviewed, changed in bulk and rebuilt at any time.

| File | Role |
|---|---|
| `planning/backlog/SCHEMA.md` | Format of a backlog fragment: epics → features → tasks, with tier, sequencing phase, story, acceptance criteria, dependencies and tasks (area, hours 1–8, description) |
| `planning/backlog/<letter>-<area>.json` | The fragments, one per group of epics |
| `planning/backlog/priorities-final.json` | The owner's tier for every feature (from a spreadsheet); the build refuses a fragment that changes a tier |
| `planning/backlog/build.py` | Validates the fragments, orders tasks by tier → sequencing phase → epic, fills 100-hour sprints (a new sprint always starts at the MVP / Good to have boundary), and writes `backlog.json` and `BACKLOG.md` |
| `planning/backlog/import_backlog.py` + `.github/workflows/import-backlog.yml` | Creates labels, sprint milestones and the issue tree on GitHub |
| `planning/backlog/reset_backlog.py` + `.github/workflows/reset-backlog.yml` | Deletes every imported issue and the sprint milestones (typed confirmation `DELETE`, dry-run option) |

**The import workflow can be re-run safely:**
- Each issue carries a hidden marker `<!-- backlog-key: E05/3.5.1/T2 -->`. Issues that already exist are never created twice.
- **Existing issues are updated** when their title, body, sprint or labels changed in `backlog.json`, for example after a re-plan moves tasks to other sprints.
- Sprint descriptions (planned hours, main epics) are updated.
- The last step adds new issues to the sprint board (section 3).

**To change the plan:** edit the fragments → `python3 planning/backlog/build.py` → commit → run **Import backlog**.

**Lessons**
- GitHub's built-in `GITHUB_TOKEN` can create and edit issues, but **it can't delete issues or manage user-owned Projects.** Those need the owner's token (section 6).
- Creating about 1,000 issues takes 1–2 hours, because the script pauses between calls to stay under GitHub's limits. Run it as a workflow, not from a laptop.
- If the design or plan is likely to change a lot, **don't import yet.** Import after sign-off, or reset and re-import.

## 3. Sprint board (GitHub Project)

`planning/backlog/setup_project.py` (also run by `.github/workflows/setup-project-board.yml`, and as the last step of the import):
- creates a **user-owned Project** named after the product, or reuses it, and links it to the repository
- adds every backlog issue to it
- creates a number field **`Estimate (h)`** and fills it for each task from its body
- writes a project README with the suggested views.

**Views must be created once by hand.** GitHub's API can't create Project views.

1. **Sprint board:**
   - Board layout, columns by **Status** (Todo / In Progress / Done).
   - Filter `milestone:"Sprint 01"`, changed each sprint.
   - Field sum: `Estimate (h)`.
2. **All sprints:** table grouped by **Milestone**, filter `has:milestone`, field sum `Estimate (h)`.
3. **Epics and features:** table, filter `no:milestone`, grouped by **Parent issue**.

The Project's built-in workflows move items to **Done** when an issue is closed. The Issues tab itself always stays a flat list; the board is where the work is followed.

## 4. Branches, pull requests and merging

- **`main` is the only long-lived branch** and is protected by a **branch ruleset**:
  - changes only through pull requests, with no direct pushes and no bypass
  - **every required check must pass** (section 5)
  - **the owner merges every pull request.** The AI assistant opens pull requests but never merges them.
- **No required approvals while working solo.** GitHub doesn't let you approve your own pull request, and pull requests opened by tools under your account count as yours. When collaborators join, require **one approval from the owner (code owners)** on their pull requests.
- **Everything goes through pull requests, planning documents included.** Document-only pull requests pass the checks quickly because path filters skip the build and deploy jobs.
- **When to switch protection on:** only after the CI workflows exist and have run once. Earlier, a ruleset that requires checks blocks every pull request, because those checks never report.

## 5. Continuous integration: required checks on every pull request

| # | Check | Runs on | When |
|---|---|---|---|
| 1 | **Build:** compile, format check, and fail if the exported OpenAPI file differs from the committed one (the mobile client is generated from it) | Linux | API or OpenAPI changes |
| 2 | **API unit tests** | Linux | API changes |
| 3 | **API integration tests** against real PostgreSQL + PostGIS + pgvector and Azurite containers (Testcontainers); AI calls use a **fake provider with canned answers** | Linux | API changes |
| 4 | **iOS unit tests** | macOS | iOS app or OpenAPI changes |
| 5 | **iOS UI tests** (XCUITest on a simulator, against a **fake API** chosen by a launch argument) | macOS | iOS app or OpenAPI changes |
| 6 | **QA deploy and smoke test** (section 7) | Linux | API changes |
| – | Android build, unit and UI tests (added with the Android app) | Linux | Android app or OpenAPI changes |

- **Path filters with a "not needed" pass:** a small gate job reports success for checks that were skipped. Otherwise a required check would stay "pending" forever on a pull request that didn't touch that area.
- **Why the iOS checks are path-filtered:** for private repositories, macOS minutes count ×10 against the free 2,000 minutes a month (about 200 real Mac minutes). Linux jobs are cheap.
- **Tests are planned work, not an afterthought.** Every feature in the backlog has explicit tasks for API unit tests, API integration tests, iOS unit tests and iOS UI tests (Android tests in each Android port), sized 1–4 h by feature size, on top of a manual "test on the phone" task.
- **A foundation feature, "Test frameworks and fakes",** comes first, before any feature work. It provides:
  - the test projects and conventions
  - the Testcontainers fixture
  - the fake AI provider
  - the fake API for UI tests
  - UI-test helpers that attach a screenshot when a test fails
  - a short testing guide.

## 6. Tokens, secrets and identity

| Credential | Used for | Notes |
|---|---|---|
| `GITHUB_TOKEN` (automatic) | Creating and editing issues, labels and milestones; commenting on pull requests; pushing images to GitHub Container Registry | Give each workflow only the `permissions:` it needs |
| Owner's **classic** personal access token, scopes `repo` + `project` (`BACKLOG_ADMIN_TOKEN` / `PROJECT_TOKEN` secret) | Deleting issues (reset), creating the user-owned Project, one-off admin set-up (rename `master` → `main`, rulesets, environments) | **Fine-grained tokens failed** for deleting issues. Give it a short expiry and **delete it once the set-up is done** |
| Azure **OIDC** federated sign-in (`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`) | Deploying to Azure from Actions | No stored passwords. Created once by a Cloud Shell script, limited to the project's resource group |
| Registry read token | Container Apps pulling private images from ghcr.io | Kept in Key Vault |

**Commit identity**
- Every commit, including the AI assistant's, is authored and committed as the owner: `git config user.name` / `user.email` with an email linked to the owner's GitHub account. The assistant adds a `Co-Authored-By` trailer, so AI-assisted commits remain visible.
- Set it in every new session. Once collaborators join, their commits show their own names.
- If history was made under another identity, rewrite it **before anyone else clones**, with `git filter-branch --env-filter` (or `git filter-repo`) and a force-push. Commit IDs change, so existing clones must re-clone.
- Issues created by workflows always show `github-actions` as their author; that can't be changed.

## 7. Deployment (API only; mobile apps are released by hand)

**Environments.** GitHub environments `qa` and `production` hold the deployment settings.

**Images.** Container images go to **GitHub Container Registry (ghcr.io)**: private and free at this size, instead of Azure Container Registry (about €4–5 a month).

**QA: one version per pull request**, on every pull request update:
1. Build the image and tag it `pr-<n>`.
2. Deploy a **Container Apps revision labelled `pr-<n>`** on the QA app. It has its own URL and scales to zero, so it costs almost nothing.
3. Create the database **`qa_pr_<n>`** if needed, apply migrations and load sample data.
4. Use a per-pull-request storage folder. The AI uses the fake provider unless switched on.
5. Run the smoke test (`/health` plus a sample endpoint), then **comment the URL on the pull request**.

When the pull request is **merged or closed**, the revision, database and files are removed. Test builds of the mobile app have a hidden setting to point at a QA URL.

**Prod: deploys when `main` changes** (merging a pull request updates `main`):
1. Build the image and push it to ghcr.io.
2. Run the database migrations.
3. Start the new revision.
4. Check `/health`.
5. Move traffic to it.

If the health check fails, traffic stays on the previous revision and the run fails. A pull request closed without merging never deploys to prod.

**Databases.** Prod and QA databases live on the **same small PostgreSQL server**, with separate databases and logins, so QA adds no cost. This is acceptable while there are no real users. Move QA to its own server when prod matters.

## 8. Set-up checklist for a new project

**Planning stage**
1. Create the repository (private) and a `CLAUDE.md` with working agreements and a decision log.
2. Copy `planning/backlog/` (SCHEMA, build, import, reset and project scripts) and the three workflows. Adjust the labels, areas and project title.
3. Write the backlog fragments, run `build.py`, review `BACKLOG.md`.
4. Add the owner's classic token (`repo` + `project`) as a repository secret.
5. Run **Import backlog**. It creates labels, sprints, issues and the board.
6. Create the three Project views by hand (section 3).

**First sprint**

7. Add the CI workflows (section 5) and the "Test frameworks and fakes" foundation.
8. Run the Azure Cloud Shell script for the OIDC sign-in, then add the three IDs as secrets in the `qa` and `production` environments.
9. Add the QA-per-pull-request and prod deploy workflows (section 7).
10. Once every check has run at least once:
    - rename `master` → `main`
    - add the **branch ruleset** (pull request required, all checks required, no bypass)
    - add a pull request template.
11. Delete the owner's classic token.

**When collaborators join**

12. Add them with write access, require **one code-owner approval** on pull requests, and keep "the owner merges".
