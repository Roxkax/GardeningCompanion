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
- **Scope:** while the app is for personal use, **every feature is essential and in scope**. Premium is only noted as a *potential* tier for the commercial phase. It never removes a feature from the plan.
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
| 2026-10-20 | **Roadmap is dynamic:** not a fixed list generated once. It continuously works out next actions from the garden's state, the actions done (including deviations) and current best practices. It covers each zone separately, is season-aware, starts from what already exists, and has time and cost estimates per action. |
| 2026-10-20 | **Roadmap engine design:** an activity log where entries are never overwritten, a state view per zone, a rules layer plus an AI layer to produce next actions, recalculation on events plus a daily check, and traceability of the content version and model behind each recommendation |
| 2026-10-20 | **Current best practice:** the knowledge base cites sources and has review dates. An AI job proposes content updates, and **a person reviews each update before it's published**. Nothing is published automatically from the web. |
| 2026-10-20 | **All features are essential** during personal use. Premium is only a *potential* tier for later commercial use. |
| 2026-10-20 | **Plot mapping:** boundary drawn by tapping or walking with GPS, zones and beds (on the map or by exact dimensions), points of interest, shade estimation, prevailing wind, layout designer, measuring tool, layout history. **Several plots per user is post-MVP** (the data model still treats the plot as its own entity). |
| 2026-10-20 | **Site assessment has no soil analysis:** no soil tests, no lab tests, no judging the soil from photos. It covers vegetation to clear, problem plants, trees to keep, obstacles, terrain, visible water problems, infrastructure, wildlife pressure, fixed photo spots, walk-around video, equipment advice and re-assessments. The soil type estimate from SoilGrids in plot mapping stays. The well water test moves to the irrigation planner. |
| 2026-10-20 | **Planting calendar:** based on climate (temperature rules applied to local climate history), with direct sow, plant-out and harvest windows. Includes too-hot windows, forecast adjustment, zone fit, varieties, day length, harvest estimates from growing degree days, staggered sowing and export to the phone calendar. **No indoor seed starting, no microclimate correction, no lunar calendar.** |
| 2026-10-20 | **New feature, choosing your crops:** the user picks crops (variety, priority, quantity) helped by suggestions ranked with fixed rules (climate, zone, water, difficulty, timing). It warns about poor fits but never blocks a choice, and estimates how much to plant. It's a Design-phase step in the roadmap, and drives the calendar, planners, irrigation, materials and assistant. |
| 2026-10-20 | **Guides:** a standard step layout, three kinds of guide (techniques, crops, problems), quantities from the user's numbers, "doing" mode with read-aloud, Ask AI and photo check per step, feedback on unclear steps, and offline text and images with videos online only. Illustrations: AI images reviewed by the owner plus diagrams now, an illustrator later. Mandatory sources, and an **expert review before the commercial launch**. |
| 2026-10-20 | **Journal and timeline:** the user-facing view of the activity log. Quick and bulk logging, voice notes, automatic entries, weather on each day, changing the date, timeline views and photo time-lapse, harvest log with comparison to expected yield and optional value, search, filters, CSV/PDF export. |
| 2026-10-20 | **Tasks and reminders:** tasks come from the roadmap, calendar, regular care, weather, AI and the user. They have date ranges, time estimates, and materials checked against the inventory. Outcomes go into the activity log. Weekend planner, weather-aware rescheduling, repeating tasks, alternatives for missed tasks, on-phone and push reminders, morning summary, quiet hours. **Sharing tasks is post-MVP.** |

## Open decisions
- Embedding model for pgvector search
- Image generation model for guide illustrations
- Sync conflict policy for each entity
- The feature-by-feature review of `PLAN.md` §3 (in progress)
