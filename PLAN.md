# Gardening Companion — Execution Plan

## 1. Vision

A mobile app that guides a complete beginner from **unused land to a productive, well-maintained vegetable garden**. It covers the whole process: assessing the land, designing the layout, preparing the soil, setting up irrigation, sowing and planting, maintenance and harvest. An AI assistant makes the guidance interactive, and it gets better over time as it learns the user's garden.

- **First user:** the author, with a plot in Alentejo, Portugal (hot, dry summers, so irrigation is critical).
- **Target:** commercial potential. The app must adapt to **any user's location and climate**.

---

## 2. Confirmed decisions

| Topic | Decision |
|---|---|
| Platforms | **Mobile only**, native: **iOS (Swift/SwiftUI)** and **Android (Kotlin/Jetpack Compose)** |
| Location | Adapts to each user's location. Alentejo is the first test case. |
| Languages | **Portuguese (pt-PT) and English** from the first version |
| Offline | Journal, tasks, materials, plot map, calendar and downloaded guides work offline. AI photo analysis is queued until the device is online. |
| AI actions | The assistant **proposes changes, which are applied only after the user confirms** |
| Satellite | The user **draws the plot and zones on a satellite map**. The app adds area, sun, slope and soil information. Automatic detection comes later. |
| Guides | **Text and illustrations, plus selected videos.** AI-generated animations come later. |
| AI provider | **Claude via Microsoft Foundry** (Azure billing), behind a provider-agnostic layer |
| Database | **PostgreSQL** with PostGIS (geospatial) and pgvector (AI search) |
| Backend | **.NET (ASP.NET Core)**. A Python service is added only if we later need our own raster or ML processing. |
| Cloud | **Azure**, with the lowest possible cost during the individual phase |
| Business model | **Freemium**: free core features, with the AI features in a premium subscription |

---

## 3. Features

The **project roadmap** is the backbone of the app. It runs through these phases: Assess → Design → Prepare soil → Irrigation → Plant → Maintain → Harvest → Plan next season. Each phase has checklists and tasks that the AI adjusts as the user makes progress.

| Feature | Approach | Tier |
|---|---|---|
| Plot mapping | Draw the plot and zones on a satellite base map (MapKit on iOS, Google Maps SDK on Android). The server calculates area and sun exposure, and adds slope from elevation data and estimated soil type from SoilGrids. | Free |
| Site assessment by camera | Claude analyzes photos for weeds, stones, slope, shade and how the soil looks. Guided DIY soil tests (jar test, squeeze test), and a recommendation for a lab test. | Premium |
| When to plant what | A climate-driven calendar: crop rules based on temperature thresholds and frost risk, rather than fixed months, so it works anywhere | Free |
| Harvest readiness | A photo, plus days since sowing and the variety's maturity, gives a verdict with a confidence level | Premium |
| Future planting planner | Rules (season windows, crop rotation by family, spacing, companion plants, succession planting) generate the plan. The AI explains and adjusts it. | Free (rules) / Premium (AI) |
| Plant identification | Claude vision first. A specialist plant-ID service is optional later. | Premium |
| Pest and disease diagnosis | The same photo-analysis pipeline as identification | Premium |
| Materials tracking | Inventory and a shopping list, generated automatically from plans (for example, an irrigation plan produces metres of drip line and fittings) | Free |
| Irrigation planner | Water needs from evapotranspiration (ET₀) × a crop coefficient (Kc) × area − rain, giving a drip layout, run times and a materials list | Free |
| Weather alerts | Frost, heatwave and wind warnings, and a notice to skip watering when rain is expected | Free |
| Improvement suggestions | A weekly AI review of the journal, photos, weather and plan | Premium |
| AI assistant | Knows the user's garden, answers from the knowledge base and proposes actions to confirm | Premium (with free quota) |
| Journal and timeline | Photos and actions for each bed, plus a harvest and yield log. This is what lets the AI get better over time. | Free |
| Guides | Step-by-step guides in PT and EN, with illustrations and selected videos, downloadable for offline use | Free |

---

## 4. Backend architecture

```
 iOS (SwiftUI + SwiftData)        Android (Compose + Room)
          │   generated OpenAPI clients   │
          └──────────────┬───────────────┘
                         ▼
        ASP.NET Core API  (Azure Container Apps, scale-to-zero)
   ┌───────────┬──────────┬──────────┬───────────┬────────────┐
   │ Core API  │ Sync API │ Media    │ AI layer  │ Knowledge  │
   │ (domain)  │ (offline)│ (SAS URLs)│ (Foundry) │ base / i18n│
   └─────┬─────┴────┬─────┴────┬─────┴─────┬─────┴─────┬──────┘
         ▼          ▼          ▼           ▼           ▼
   PostgreSQL + PostGIS + pgvector     Blob Storage    Claude (Foundry)
         ▲                                  ▲
         └──── Worker (Container Apps Jobs / queue) ─────┐
               thumbnails · AI jobs · weather alerts ·   │
               weekly reviews · reminders  ──► Notification Hubs (APNs/FCM)
   External data: Open-Meteo (weather, climate, ET₀, elevation) · SoilGrids (soil)
   Identity: Entra External ID (email, Sign in with Apple, Google)
```

### Components
1. **Identity:** Entra External ID, signed in with MSAL on both apps. Multi-user from day one, with every record scoped to a user.
2. **Core API:** plots, zones and beds (PostGIS geometry), plantings, tasks, journal, materials, plans, roadmap progress. Built with ASP.NET Core and EF Core, using NetTopologySuite for geometry.
3. **Sync API:** offline-first sync.
   - Clients generate the record IDs (UUIDs).
   - Every record carries a server version number.
   - Deleted records are marked as deleted (soft deletes) rather than removed.
   - Endpoints are `POST /sync/push` and `GET /sync/pull?since=<token>`.
   - Conflicts are resolved by last-write-wins per record, and every resolution is logged.
4. **Media:** the API issues short-lived SAS upload URLs, the phone uploads directly to Blob Storage, and a queue triggers thumbnail creation and any AI analysis.
5. **AI layer:** one `IAiService` handles every task: site assessment, identification, diagnosis, harvest readiness, assistant chat (tool use that creates **pending proposals**), plan explanation and the weekly review.
   - It assembles the context for each call: garden, history, weather, and relevant knowledge-base content.
   - Usage is limited per user according to their plan tier.
   - Every request is logged with its cost.
   - The model can be swapped.
6. **Knowledge base:** crops (temperature thresholds, frost tolerance, days to maturity, rotation family, spacing, Kc), techniques and guides.
   - The **source of truth lives in git** under `content/` as YAML and Markdown, in both PT and EN.
   - A pipeline publishes it to the database and Blob Storage, and builds offline packages.
   - The AI uses it as grounding: PostgreSQL full-text search first, then pgvector embeddings.
7. **External data adapters:** Open-Meteo (forecast, historical climate, ET₀, elevation) and SoilGrids (soil). The results are cached for each plot.
8. **Worker:** queue processing and scheduled jobs (weather alerts, reminders, weekly reviews).
9. **Notifications:** Azure Notification Hubs (free tier), sending to APNs and FCM.
10. **Later:** App Store and Play subscription receipt validation, IoT and sensor ingestion, a content admin interface, and a Python service for raster or ML work.

### Estimated monthly cost during the individual phase
To be verified against current Azure pricing.

| Service | Estimate |
|---|---|
| Container Apps (API and jobs, consumption plan) | ~€0, within the monthly free grant |
| PostgreSQL Flexible Server (Burstable B1ms) | Free for 12 months on a new Azure account, then ~€12–15. It can be stopped when idle. |
| Blob Storage | < €1 |
| Entra External ID | Free at low user counts |
| Notification Hubs | Free tier |
| Key Vault, Application Insights | ~€0–2 (with sampling) |
| Claude via Foundry | Pay per use, a few € at personal usage |
| **Total** | **~€5 during the first year, ~€20 after** |

Local development runs in Docker (PostgreSQL + PostGIS, Azurite for storage) at no cost.

---

## 5. Repository layout

```
backend/   .NET solution: Api, Domain, Infrastructure, Worker, tests
ios/       SwiftUI app (SwiftData, MSAL, MapKit)
android/   Kotlin/Compose app (Room, MSAL, Google Maps SDK)
content/   crops and guides (YAML/Markdown, pt-PT + en)
infra/     Bicep templates for Azure
docs/      architecture decisions (ADRs), API notes
```

---

## 6. Milestones

Each milestone ships backend and app work together and ends with something usable on the real plot in Alentejo.

### M0 — Foundations
- [ ] Repo structure, .NET solution, Docker Compose (PostgreSQL + PostGIS + Azurite)
- [ ] CI: build, test, lint for the backend and both apps, plus OpenAPI client generation
- [ ] Entra External ID set up, with sign-in working on iOS and Android
- [ ] Bicep templates for Container Apps, PostgreSQL, Blob Storage, Key Vault and Notification Hubs
- [ ] i18n scaffolding (pt-PT and en) in the backend and both apps
- [ ] Account deletion and data export endpoints, which the app stores require

### M1 — Plot and roadmap
- [ ] Draw the plot and zones on a satellite map, stored in PostGIS
- [ ] Enrichment: area, sun exposure, slope (elevation data) and soil estimate (SoilGrids)
- [ ] Project roadmap with phases and checklists (static content first)

### M2 — Journal, tasks, materials and offline sync
- [ ] Local databases (SwiftData and Room), plus the sync push/pull protocol
- [ ] Journal with photos (SAS upload and thumbnails), tasks with reminders, materials inventory and shopping list

### M3 — Knowledge base, calendar and guides
- [ ] `content/` pipeline publishing to the database and Blob Storage, with offline packages
- [ ] Crop catalog (30–50 crops relevant to Mediterranean climates first), PT and EN
- [ ] Climate-driven sowing and planting calendar
- [ ] First guides: soil preparation, compost, drip irrigation, sowing, transplanting

### M4 — AI photo features
- [ ] AI layer on Foundry, with quotas by plan tier and cost logging
- [ ] Site assessment, plant identification, pest and disease diagnosis, harvest readiness
- [ ] Offline photo queue, with push notifications when results are ready
- [ ] An evaluation set of real photos from the plot, re-run whenever a prompt or model changes

### M5 — AI assistant and smart alerts
- [ ] An assistant with garden context that answers from the knowledge base
- [ ] Tool use that creates pending proposals, a confirmation interface and an audit log
- [ ] Weather alerts and the weekly improvement review

### M6 — Planning
- [ ] Planner for rotation, succession and companion planting
- [ ] Irrigation planner (ET₀ × Kc) that generates a materials list
- [ ] Next-season planning from the harvest and yield history

### M7 — Commercial readiness
- [ ] Freemium tiers with App Store and Play subscriptions (server-side receipt validation)
- [ ] Commercial licences for data sources (Open-Meteo paid plan or an alternative, and the plant-ID service if used)
- [ ] Privacy policy, GDPR review, AI disclaimers (especially around pesticides and chemicals), store listings

---

## 7. Licensing to verify before going commercial

- Satellite map tiles (Apple, Google) may be displayed, but not analyzed by AI or stored.
- Open-Meteo's free API is non-commercial only. It needs a paid plan or an alternative.
- SoilGrids is CC-BY, so it needs attribution. Check the API's rate limits.
- Specialist plant-ID APIs (Pl@ntNet, Kindwise): their free tiers are non-commercial.
- Check the availability and pricing of Claude models in Microsoft Foundry.

---

## 8. Open decisions

- [ ] **Which platform first?** A solo developer building two native apps should finish the vertical slice on one platform, then port it.
- [ ] Embedding model for pgvector search. Claude doesn't produce embeddings, so this needs a separate model, for example one on Foundry.
- [ ] The exact sync conflict policy for each entity (last-write-wins per record or per field).
