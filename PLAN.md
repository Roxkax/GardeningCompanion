# Gardening Companion — Execution Plan

**Goal:** A personal/learning project. A web + mobile app for tracking plants, identifying them and getting AI advice, and planning when to plant.

**Guiding principles**
- Ship a thin, usable slice early, then add to it. Each milestone ends with something you actually use in your garden.
- Use one codebase where it's cheap and only split it when there's a real reason.
- Use managed services for anything that isn't the interesting part (auth, storage, hosting), so the effort goes into the features.

---

## 1. Recommended stack

| Layer | Choice | Why |
|---|---|---|
| Client (web + iOS + Android) | **Expo (React Native) + Expo Router**, TypeScript | One universal codebase runs on all three platforms. The camera and photo library work natively. |
| UI | Tamagui or NativeWind | Cross-platform styling that also looks right on the web. |
| Backend | **Supabase**: Postgres, Auth, Storage, Edge Functions | Auth, a database, image storage and server functions with almost no ops work. Row-Level Security keeps each user's data private. |
| AI | **Claude API** (vision + chat), called only from Edge Functions | Identifies plants and diagnoses problems from photos, plus a chat assistant that knows your garden. The API key never reaches the client. |
| Climate data | **Open-Meteo** (free, global) | Historical temperatures, used to estimate last and first frost dates for any location. |
| Plant/crop data | A curated `crops.json` seed (about 40–60 common plants) | Sowing rules relative to frost dates. You control the data, and it avoids flaky third-party plant APIs. |
| Data fetching | TanStack Query + generated Supabase types | Typed queries, caching and optimistic updates. |
| Validation | Zod (shared schemas) | One source of truth for client and server. |
| Tooling | pnpm, ESLint, Prettier, Vitest, GitHub Actions | Standard and fast. |
| Releases | EAS Build/Update (mobile), Vercel or Netlify (web export) | |

**Alternative if you'd rather learn Next.js:** use a Turborepo monorepo with `apps/web` (Next.js), `apps/mobile` (Expo) and `packages/shared` (types, Zod, API client). You get a better web experience, but roughly twice the UI work. Expo-universal is the better fit for a personal project.

---

## 2. Data model (first draft)

```
profiles        id (= auth.uid), display_name, location_lat, location_lon,
                last_frost_date, first_frost_date, units
gardens         id, user_id, name, notes
beds            id, garden_id, name, type (raised/in-ground/container), sun (full/part/shade)
plants          id, user_id, bed_id?, common_name, species?, crop_id?, variety,
                planted_on, status (planned/sown/growing/harvested/removed), notes
plant_photos    id, plant_id, storage_path, taken_at
journal_entries id, plant_id, kind (water/fertilize/prune/pest/harvest/note), body, created_at
ai_queries      id, user_id, plant_id?, kind (identify/diagnose/chat), input, result_json, created_at
crops           (seeded, read-only) id, name, sow_indoors_weeks_before_frost,
                direct_sow_weeks_after_frost, transplant_weeks_after_frost,
                days_to_maturity, spacing_cm, sun, notes
```
Every user table gets an RLS policy of `user_id = auth.uid()` (directly or through its parent).

---

## 3. Milestones

Estimates assume part-time work, about 8–10 hours a week. Adjust them freely.

### M0 — Foundations (week 1)
- [ ] Initialize the Expo app (TypeScript, Expo Router) and confirm it runs on web, iOS and Android
- [ ] Set up ESLint, Prettier, Vitest, and a GitHub Actions CI job (lint, typecheck, test)
- [ ] Create the Supabase project and the local dev setup (`supabase start`, migrations in git)
- [ ] Auth: email magic link (add Apple/Google later), plus a `profiles` row created on signup
- [ ] Generate typed Supabase client types from the schema

**Done when:** you can sign in on the phone and in the browser and see an empty "My Garden" screen. CI is green.

### M1 — Plant tracker (weeks 2–4)
- [ ] Create, read, update and delete gardens, beds and plants
- [ ] Photo upload (camera and library) to Supabase Storage, with client-side resizing
- [ ] Plant detail screen: a photo timeline and journal entries
- [ ] Quick actions: "watered", "fertilized" and "harvested" log entries in one tap
- [ ] RLS policies, plus tests that one user can't read another user's data

**Done when:** you've added your real garden and are logging activity in it.

### M2 — Planting calendar (weeks 5–6)
- [ ] Location: device GPS or manual entry, saved to the profile
- [ ] Edge Function: Open-Meteo historical data → estimated last and first frost dates, cached on the profile and overridable by the user
- [ ] Seed `crops.json` with the plants you actually grow first
- [ ] Calendar view: "This month: start indoors / direct sow / transplant", computed from frost dates and the crop rules
- [ ] "Plan it": add a crop from the calendar as a `planned` plant

**Done when:** the app tells you correctly what to sow this month where you live.

### M3 — AI: identify, diagnose, ask (weeks 7–9)
- [ ] Edge Function `identify`: photo → species candidates with confidence, as structured JSON output
- [ ] Edge Function `diagnose`: photo plus plant context (species, age, recent journal) → likely issues, causes and next steps
- [ ] Chat assistant that has the context of your garden, plants and location/season
- [ ] Save results to `ai_queries`. One tap applies an identification to a plant.
- [ ] Guardrails: per-user daily rate limit, image size cap, and a reminder that AI advice can be wrong
- [ ] A small eval set: 20–30 of your own photos with known answers, re-run whenever a prompt changes

**Done when:** you photograph a plant and get a useful identification or diagnosis, and you can ask "what should I do this week?"

### M4 — Polish and stretch goals (week 10+)
- [ ] Care reminders with push notifications (Expo Notifications plus a scheduled Edge Function)
- [ ] Offline-friendly logging: queue writes and sync when back online
- [ ] Weather-aware tips, such as a frost warning or "skip watering, rain expected"
- [ ] Bed layout or spacing visualizer
- [ ] Data export (CSV/JSON)

---

## 4. Key risks and how to handle them

| Risk | Mitigation |
|---|---|
| React Native Web quirks | Test on the web every milestone, not only at the end. Keep platform-specific code in `*.web.tsx` files. |
| AI misidentifies a plant or gives bad advice | Show confidence and alternatives, keep a human confirmation step, and maintain the eval set. |
| AI cost creeps up | Resize images before upload, cache results, rate-limit, and use a smaller model for chat and a stronger one for hard diagnoses. |
| Frost-date estimates are wrong | Let the user override them, and show the source and method. |
| Scope creep | Every new idea goes into the M4 backlog. Finish the current milestone first. |

---

## 5. How to work

- **Branches and PRs:** one feature branch per checklist item or small group of items, merged after CI passes.
- **Issues:** turn each checklist item into a GitHub issue, with a milestone per M0–M4.
- **Migrations:** every schema change goes in a SQL migration in `supabase/migrations/`. Never edit the database by hand.
- **Weekly check-in:** what shipped, what's blocking you, and what's next. Re-plan the next milestone, not the whole project.

---

## 6. Open decisions

- [ ] Expo-universal (recommended) or Next.js + Expo monorepo?
- [ ] UI library: Tamagui or NativeWind?
- [ ] Your location and climate. This decides which crops to seed first.
- [ ] Self-hosted Supabase or the hosted free tier? Hosted is recommended to start.
