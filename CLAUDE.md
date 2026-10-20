# CLAUDE.md — Gardening Companion

## Project
A native mobile app that guides a complete beginner from unused land to a productive, well-maintained vegetable garden ("horta"), with an AI assistant that makes the guidance interactive and improves as it learns the user's garden. The first user is the project owner, whose plot is in Alentejo, Portugal. The app is built with commercial potential in mind.

- **`PLAN.md`** is the detailed execution plan: features, architecture, milestones and cost.
- **This file** holds the working agreements and the decision log. Record every decision the owner confirms here.

## Current phase: PLANNING
- **Do not write application code, scaffold projects or create GitHub issues** until the owner explicitly says planning is complete.
- The plan is being reviewed **one feature at a time**. The owner may change or add features. Update `PLAN.md` and the decision log after each confirmed change.

## Working agreements
- **Language:** reply in English. The owner may write in Portuguese.
- **Ask one question at a time.** Don't send batches of questions.
- **Requirements flow:** the owner describes features from the mobile user's point of view. Claude works out what the backend needs and **confirms it with the owner before treating it as decided**.
- **Feasibility:** be honest about limits (e.g. AI can't measure soil pH from a photo) and propose realistic alternatives.
- **Cost:** keep Azure costs as low as possible during the individual phase. Prefer pay-per-use and scale-to-zero services.
- **Commercial readiness:** design for multiple users from day one, and flag licensing or terms-of-service issues for commercial use.
- **Git:** commit and push planning documents to `master` after each confirmed change.

## Work tracking on GitHub
The owner is used to Azure DevOps, so the same hierarchy is used, built with sub-issues:
- **Epic:** a big area. Use an Epic issue type if one is available, otherwise a Feature issue with an `epic` label.
- **Feature:** the equivalent of a DevOps PBI. A user-facing capability with acceptance criteria. A sub-issue of an Epic.
- **Task:** one concrete step to deliver a Feature. A sub-issue of a Feature.
- **Labels** mark the area: `area:backend`, `area:ios`, `area:android`, `area:content`, `area:infra`.
- **Milestones** are M0–M7 from `PLAN.md`.
- The owner creates the milestones, the Project board and any Epic type in the GitHub UI. Claude creates the issues and sub-issue links, **only after the owner approves the written breakdown**.

## Decision log
| Date | Decision |
|---|---|
| 2026-10-19 | Personal project for now, with commercial potential |
| 2026-10-20 | **Mobile only**, with **native** apps: Swift/SwiftUI (iOS) and Kotlin/Jetpack Compose (Android) |
| 2026-10-20 | **iOS first**. Each milestone is ported to Android once it's stable. |
| 2026-10-20 | The app adapts to **each user's location**. Alentejo is the first test case. Climate and weather data must cover the whole world. |
| 2026-10-20 | **Portuguese (pt-PT) and English** from the first version |
| 2026-10-20 | **Offline:** journal, tasks, materials, plot map, calendar and downloaded guides. AI photo analysis is queued until the device is online. |
| 2026-10-20 | **AI assistant proposes changes, which are applied only after the user confirms.** Every change is logged. |
| 2026-10-20 | **Satellite:** the user draws the plot and zones on the map. The app adds area, sun, slope and soil. Automatic detection comes later. |
| 2026-10-20 | **Guides:** text, illustrations and selected videos. AI-generated animations come later. |
| 2026-10-20 | **AI provider:** Claude via Microsoft Foundry, behind a provider-agnostic layer |
| 2026-10-20 | **Database:** PostgreSQL with PostGIS and pgvector |
| 2026-10-20 | **Backend:** .NET (ASP.NET Core). Python is added only if we later need our own raster or ML processing. |
| 2026-10-20 | **Cloud:** Azure, with costs kept minimal during the individual phase |
| 2026-10-20 | **Business model:** freemium. Core features are free and AI features are premium. AI usage limits are tied to the plan tier from day one. |
| 2026-10-20 | **Work tracking:** GitHub issues in an Epic → Feature → Task hierarchy, using sub-issues |

## Open decisions
- Embedding model for pgvector search
- Sync conflict policy for each entity
- The feature-by-feature review of `PLAN.md` §3 (in progress)
