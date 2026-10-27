# Gardening Companion — Execution Plan

## 1. Vision

A mobile app that guides a complete beginner from **unused land to a productive, well-maintained vegetable garden**. It covers the whole process: assessing the land, designing the layout, preparing the soil, setting up irrigation, sowing and planting, maintenance and harvest. An AI assistant makes the guidance interactive, and it gets better over time as it learns the user's garden.

- **First user:** the author, with a plot in Alentejo, Portugal (hot, dry summers, so irrigation is critical).
- **Target:** commercial potential. The app must adapt to **any user's location and climate**.

---

## 2. Confirmed decisions

| Topic | Decision |
|---|---|
| Platforms | **Mobile only**, native: **iOS (Swift/SwiftUI)** and **Android (Kotlin/Jetpack Compose)**. **iOS is built first**, and each milestone is ported to Android once it's stable. |
| Location | Adapts to each user's location. Alentejo is the first test case. |
| Languages | **Portuguese (pt-PT) and English** from the first version |
| Offline | Journal, tasks, tools, plot map, calendar and downloaded guides work offline. AI photo analysis is queued until the device is online. **Prioritised as Good to have** (see §6). |
| AI actions | The assistant **proposes changes, which are applied only after the user confirms** |
| Satellite | The user **draws the plot and zones on a satellite map**. The app adds area, sun, slope and soil information. Automatic detection comes later. |
| Guides | **Text and illustrations, plus selected videos.** AI-generated animations come later. |
| AI provider | **Claude via Microsoft Foundry** (Azure billing), behind a provider-agnostic layer |
| Database | **PostgreSQL** with PostGIS (geospatial) and pgvector (AI search) |
| Backend | **.NET (ASP.NET Core)**. A Python service is added only if we later need our own raster or ML processing. |
| Cloud | **Azure**, with the lowest possible cost during the individual phase |
| Business model | **Freemium** (later): free core features, with the AI features in a premium subscription |
| Scope while it's for personal use | **All features are essential and in scope.** The tier column only notes what *could* be premium once the app goes commercial. |

---

## 3. Features

### 3.1 Project roadmap (the backbone)

The roadmap guides the user from bare land to a working garden. It is **not a fixed list of steps that is generated once and stored**. It is a **dynamic process**: it takes in the current state of the garden and everything the user has done (including deviations from the plan), and works out the next actions from that. It always reflects the current state and current best practices.

- **Phases as orientation, not a script:** Assess → Design → Prepare soil → Irrigation → Plant → Maintain → Harvest → Plan next season. A zone's phase is **worked out from its state**, not tracked as a pointer through a list. After the first season, the cycle continues from "Plan next season".
- **Per zone:** each zone can be at a different stage. For example, zone A is ready to plant while zone B is still being cleared.
- **Starting point:** when setting up, the app asks what already exists (cleared land, irrigation, beds, plants), so experienced users don't start from zero.
- **Season-aware:** actions have ideal time windows for the local climate (for example, preparing soil in autumn before the rains in Alentejo), and are scheduled around them.
- **Time and cost estimates** for each action, to help plan weekends and a budget.
- **Deviations:** the user can mark an action as done differently, skipped, not possible, or as having a problem. The next actions adapt to that.
- Each action links to its guide, its tasks and the tools it needs. Consumables such as compost or seeds are mentioned for information only.
- **Choosing crops** is a step in the **Design** phase, after mapping and site assessment (see §3.6). Next actions follow the user's chosen crops.
- **How next actions are produced:** a rules layer (agronomy logic and safety limits) suggests the possible actions and their time windows. An AI layer ranks them, adapts them to deviations, explains why, and estimates time and cost. See §4, component 3.
- **Potential tier (commercial):** rules-based next actions free, AI adaptation premium.

### 3.2 Other features

All features are in scope for development. The last column only notes what could be premium in a future commercial version.

| Feature | Approach | Potential tier (commercial) |
|---|---|---|
| Plot mapping | See §3.3 | Free |
| Site assessment by camera | See §3.4 | Premium |
| Choosing your crops | See §3.6 | Free (rules) / Premium (AI explanation) |
| When to plant what | See §3.5 | Free |
| Harvest readiness | See §3.15 | Premium (checklists, notices and guides: Free) |
| Season planner | See §3.16 | Free (rules) / Premium (AI goals) |
| Plant identification | See §3.13 | Premium |
| Pest and disease diagnosis | See §3.14 | Premium (risk warnings and scouting tasks: Free) |
| Tools | See §3.10 | Free |
| Irrigation planner | See §3.11 | Free |
| Weather alerts | See §3.12 | Free |
| Improvement suggestions | See §3.18 | Premium (statistics-only report: Free) |
| AI assistant | See §3.17 | Premium (with free quota) |
| Journal and timeline | See §3.8 | Free |
| Tasks and reminders | See §3.9 | Free |
| Guides | See §3.7 | Free (Ask AI and photo check: Premium) |

### 3.3 Plot mapping

- **Satellite map** centred on the user's location: MapKit on iOS, Google Maps SDK on Android.
- **Plot boundary:** draw it by tapping corners on the map, or **walk the perimeter with GPS** (accurate to about 3–5 m, enough for the plot outline).
- **Zones and beds** drawn inside the plot, with names. Beds can also be entered with **exact dimensions** (e.g. 1.2 m × 6 m), because satellite and GPS accuracy isn't enough for small beds.
- **Points of interest:** water sources (well, borehole, tap, rain tank), electricity, gates and access, buildings, and trees. Each type has a **details panel**: trees are picked from a regional tree catalogue with pictures (or identified from a photo), with a height slider and keep or remove; water sources record the kind and how water comes out, with a "Measure flow" button for the bucket test.
- **Automatic enrichment (backend):** area, sun exposure from the location, slope from elevation data, and an estimated soil type from SoilGrids.
- **Shade:** estimated from marked trees and buildings (height plus the sun's path over the day and year), and combined with shade the user has observed and marked (e.g. "afternoon shade").
- **Prevailing wind** from weather data, used to suggest windbreaks.
- **Layout designer:** beds with real dimensions, path widths and row direction (north–south suggested for even sun).
- **Measuring tool:** distances on the map (e.g. from the well to zone A), which feed the irrigation parts list (metres of pipe).
- **Layout history:** each season's layout is kept as a version, which the crop rotation planner needs.
- **Offline:** shapes and points can be edited offline, but the satellite images may not load, because Apple and Google limit offline caching.
- **Later (not in MVP):** several plots per user. The data model includes the plot as its own entity from the start, so adding this later is cheap.

### 3.4 Site assessment by camera

For each zone, the app works out what's there now, what needs clearing or fixing, and how much effort it will take. **No soil analysis:** no soil tests, no lab tests, and no judging the soil from photos.

- **The AI looks at photos of each zone for:**
  - Vegetation to clear (type, density, height), with a suggested method (by hand, brush cutter or tractor) and a time and cost estimate.
  - Problem plants that need special removal (brambles, Bermuda grass, giant cane).
  - Trees and plants worth keeping (olive and fruit trees).
  - Obstacles: stones, rubbish, old structures and debris.
  - Terrain: slope, uneven ground, erosion, and whether terracing or levelling is needed.
  - Visible water problems: pooling and runoff.
  - Existing infrastructure: fences, gates and water points, and their condition.
  - Wildlife pressure: rabbits, wild boar, birds and moles, which decide whether fencing or netting is needed.
- **Guided photos with fixed photo spots** on the map, for before-and-after comparisons.
- **Walk-around video:** the app picks the best frames for the AI.
- **Equipment advice:** buy, rent or borrow, based on the work needed and the plot size. Follows the "always own" setting in §3.10.
- **Re-assessments** at any time, to track progress.
- **Backend:** a stored assessment for each zone, with photos, AI findings (each with a confidence level) and estimates. Every assessment is recorded in the activity log, so the roadmap updates.

### 3.5 Planting calendar

Shows what to sow or plant, and when, for the user's exact location, kept up to date with the weather. **No indoor seed starting** and **no microclimate correction.**

- **Based on climate, not fixed months:** crop rules (minimum soil temperature to germinate, minimum air temperature to plant out, frost and heat tolerance) are applied to 30 years of local climate data, so the calendar works anywhere.
- **Windows for each crop:** sow directly, plant out (seedlings bought from a nursery), and expected harvest.
- **Too-hot windows as well as frost:** for crops that go to seed in heat (lettuce, spinach), and for tomatoes, which stop setting fruit above about 35 °C. In Alentejo, autumn and winter are the main season for brassicas, lettuce and broad beans.
- **Views:** a month calendar and a "What to do this week" list.
- **Adjusted by the forecast:** for example, planting out is pushed back when a cold snap is coming.
- **Your crops first:** shows the user's chosen crops (§3.6) by default, plus a "Suggested for now" section for discovering others.
- **Fits each zone:** "what can I plant now in zone A", based on its sun and shade.
- **Varieties:** early and late varieties mature at different times. The user picks a variety or uses a generic default.
- **Day length:** suggests varieties suited to the latitude (e.g. short-day onions in southern Portugal).
- **Harvest estimates** from the heat each planting has actually received since sowing (growing degree days), not a fixed number of days.
- **Staggered sowing reminders** (e.g. lettuce every 2–3 weeks) for a continuous harvest.
- **Export** to the phone's calendar.
- Adding a crop from the calendar creates a planned planting, which updates the roadmap and tasks.
- **Backend:** crop rules in the knowledge base, local climate history fetched once per plot and cached, a fixed calculation of windows (no AI), and a daily job for harvest estimates and forecast adjustments. The result is cached on the phone for offline use.

### 3.6 Choosing your crops

The user chooses which crops to grow, helped by suggestions ranked by suitability for their location. The list shapes the rest of the app.

- **Browse and pick** from the crop catalog, optionally with a variety. Each crop gets a **priority** (must-have or nice-to-have) and a **rough quantity**.
- **Ranked suggestions with a reason**, based on:
  - Climate: heat and frost tolerance, and season length.
  - Zone conditions: sun and shade, and available space.
  - Water needs: drought-tolerant crops rank higher where water is scarce.
  - Difficulty: beginner-friendly crops are marked.
  - Timing: what can be sown soon.
- **Warnings** for a poor fit, with a better time or variety suggested. The user's choice is **never blocked**.
- **How much to plant:** the number of plants and space needed, from the desired quantity and typical yields.
- **Editable at any time.** Every change goes into the activity log, so the roadmap, calendar and planners recalculate.
- **Effect on other features:**
  - Roadmap: the Design-phase step.
  - Calendar: the user's crops first.
  - Layout designer and season planner: assign crops to beds.
  - Irrigation planner: water needs.
  - Guides and tasks: the seed and seedling quantities needed, for information only.
  - AI assistant: proposes additions or swaps, which the user confirms.
- **Backend:**
  - A "my crops" list for each user (crop, variety, priority, quantity).
  - A **suitability score** worked out with fixed rules (no AI), so suggestions work offline.
  - Space estimates from typical yields and spacing.
  - Potential premium: a personalised AI explanation of the suggestions.

### 3.7 Guides

The "how to" behind every roadmap action. Each roadmap action opens its guide.

- **Step-by-step guides in PT and EN**, with illustrations, diagrams and selected videos. Each guide cites its sources and shows a "last reviewed" date.
- **Standard layout for every step:** what to do, an illustration, tools needed, consumables needed (for information only), time needed, safety notes, common mistakes, and "how to tell it's done right".
- **Three kinds of guide:**
  - Techniques: clearing, building beds, drip irrigation, mulching, composting, sowing, planting out, staking, pruning.
  - Crop guides: each crop from sowing to harvest.
  - Problem guides: pests and diseases, organic methods first.
- **Uses your numbers:** quantities and measurements calculated from the user's data (e.g. "for your 1.2 × 6 m bed you need 14 m of drip line and 3 bags of compost").
- **"Doing" mode:** big text, one step at a time, and steps read aloud with the phone's built-in voice (free and offline). Ticking off a step records it in the activity log.
- **Ask the AI about a step** (potential premium).
- **Photo check of the work** at a step, reviewed by the AI (potential premium).
- **"This step was unclear" feedback**, which feeds the content review.
- **Offline:** text and images are downloaded. Videos are links (YouTube etc.) and only play online. A job periodically checks for broken video links.
- **Illustrations:**
  - Now: AI-generated images from **OpenAI gpt-image via Azure OpenAI** (Claude can't generate images), each reviewed by the owner, plus simple diagrams we draw. The same model makes the tool reference images (§3.10). Images are generated once when content is authored, not for each user.
  - Commercial phase: a commissioned illustrator.
- **Accuracy:** citing reputable sources is mandatory. The owner reviews guides for clarity, and **an expert (e.g. an agronomist) reviews them before the commercial launch**.
- **Authoring:** guides are drafted by AI from cited sources and reviewed by the owner, then published through the `content/` pipeline.

### 3.8 Journal and timeline

The record of everything that happens in the garden, and what the AI and roadmap learn from. It works fully offline.

- **Entries for each zone, bed or planting:** watering, feeding, sowing, planting out, weeding, mulching, pruning, treating, harvesting, observations and problems, with photos and notes.
- **Quick logging:** one tap for common actions, and logging several beds at once (e.g. "watered all of zone A").
- **Voice notes:** dictated in the field and turned into text by the phone's built-in speech recognition (free and offline).
- **Automatic entries:** completing a roadmap action, task or guide step adds a journal entry.
- **Weather on every day:** the day's rain and temperatures are attached automatically.
- **Changing the date** to log things after the fact.
- **Timeline views** for a zone, bed or planting, plus a photo time-lapse from the fixed photo spots.
- **Harvest log:** weight or count for each crop and variety, compared with what was expected, with season totals. Optional estimated value, using prices the user enters.
- **Search and filters**, and **export** to CSV or PDF.
- **Backend:** the journal is the user-facing view of the **activity log**, so there's one source of truth and sync stays conflict-free. Photos go through the media service.

### 3.9 Tasks and reminders

The garden to-do list: what to do and when, with reminders. It works offline.

- **Where tasks come from:** accepted roadmap next actions, the calendar, regular care (watering from the irrigation plan, feeding), weather alerts, confirmed AI proposals, and tasks the user adds.
- **Each task has:** its zone, bed or planting; a **date range** rather than a fixed day; estimated time; priority; a link to the guide; the **tools needed, checked against the user's tools**, with a warning if one is missing; and any consumables needed, for information only.
- **Completing tasks:** done, skipped, or couldn't do (with a reason). Each outcome goes into the activity log, so the roadmap adapts.
- **Views:** Today, This week, and by zone.
- **Week planner ("Plan your week"):** the user sets the hours available for each day of next week (Mon–Sun), with "Same as last week" and a one-tap "Day off" per day. The app spreads the most important tasks across the days by window, weather and size. A **Monday reminder** asks the user to plan next week, and a **"Plan next week" card on Today** escalates green (Mon–Wed), amber (Thu–Fri) and orange (Sat–Sun) until it's done. Planned tasks are written to a separate **"Garden" calendar** on the phone and kept in sync; the app never reads the user's calendar.
- **Weather-aware rescheduling:** skip watering before rain, water early in a heatwave, postpone spraying in wind.
- **Repeating tasks.**
- **Missed tasks:** when a time-sensitive task is missed, the roadmap engine suggests an alternative.
- **Reminders:** scheduled on the phone (works offline), push notifications from the server for weather-driven alerts, a daily morning summary instead of many notifications, and quiet hours.
- **Later (not in MVP):** sharing tasks with family or helpers.
- **Backend:** tasks are editable records (covered by the sync conflict policy) that remember where they came from. A scheduled job handles the morning summaries, weather rescheduling and push notifications.

### 3.10 Tools

Which tools the user has, which they'll need, and when. **No consumable or stock tracking:** compost, seeds, drip line and similar are only mentioned in guides and tasks as information (e.g. "about 3 bags of compost for this bed"). There's no inventory or cost tracking.

- **Images for identification:** every tool in the catalog has a **reference image**, so a beginner can recognise it (e.g. what a hoe or a mattock looks like). Images appear wherever a tool is mentioned: in guides, tasks, the "tools to get" list and the starter toolkit.
- **My tools:** a simple list of owned tools (no quantities), each shown with its reference image. The user can replace it with their own photo of their actual tool. Optionally records where it's kept.
- **Tools needed for each action:** roadmap actions, tasks and guides list their tools. The app compares them with the user's list and flags missing tools before they're needed.
- **"Tools to get" list:** missing tools, ordered by when they're needed, each marked buy, rent or borrow.
- **"Always own" setting (opt-in):** when on, every missing tool defaults to **buy**, and rent or borrow suggestions are hidden. The buy/rent/borrow information is still kept. **The owner uses this setting.**
- **Starter toolkit:** a recommended set for the plot size and planned work, split into essential and nice to have.
- **Buy vs rent vs borrow advice** for big equipment (e.g. a rototiller), unless "always own" is on.
- **Tool maintenance reminders** (sharpening, cleaning, storing irrigation parts before frost), which become tasks.
- **Later (post-MVP, commercial):** shop links or affiliate partnerships.
- **Backend:** a tool catalog in the knowledge base (reference image, purpose, typical price range, usually rented or bought; images included in the offline guide packages), the user's tool list, tools required by each action and guide, the missing-tools calculation, and the user's preference setting. Works offline.

### 3.11 Irrigation planner

Designs the watering system and says when, and roughly how long, to water. **No water needs calculation (ET₀ × Kc), no water budget, and no water quality check.**

- **Water sources** from the map's points of interest (well, mains tap, tank), with a **bucket test** to measure flow rate (time to fill 10 L). The test opens from three places: "Measure flow" in the water point's details, "Measure again" in the irrigation flow check, and a roadmap task ("Measure your well's flow", about 5 min) created the first time irrigation is planned. Until it's done, the flow check shows "Flow not measured yet".
- **Recommended method for each bed:** drip line, individual drippers, soaker hose or micro-sprinklers. Drip is the default for dry climates such as Alentejo.
- **System layout on the map:** main pipe from the source (lengths from the measuring tool), branch lines, and drip lines along each bed's rows, with dripper spacing for each crop.
- **Flow check:** if the source can't supply everything at once, the system is split into sectors that run one after another. Includes a filter (vital with well water), a pressure regulator and a backflow preventer.
- **Parts list** for the layout, for information only.
- **Watering schedule:** run times from standard guidance for each crop and season in the knowledge base, adjusted by the weather (skip before rain, more in heatwaves), early morning recommended. Creates watering tasks automatically. The user fine-tunes from observation, with help from the journal and AI.
- **Hand-watering guidance** for each crop and season, before a system is installed.
- **Mulching advice** to reduce water use.
- **Rainwater harvesting estimate:** roof area of buildings on the map × local rainfall gives litres that could be collected, plus a suggested tank size.
- **Seasonal reminders:** flush lines, clean filters, drain before frost.
- **Later (not in MVP):** smart irrigation controllers and soil moisture sensors.
- **Backend:**
  - Water sources and their flow rates.
  - An irrigation system model on the map (sectors, pipes and drip lines linked to beds).
  - Fixed calculations (no AI) for the flow check, sectors, parts list and rainwater estimate.
  - Watering guidance in the knowledge base.
  - A daily job that adjusts the schedule to the weather and creates watering tasks.

### 3.12 Weather alerts

Warns when weather is coming that could harm the garden, and says what to do about it.

- **Alert types:** frost, heatwave, strong wind, heavy rain, hail and storms, long dry spells, rain coming (skip watering), and **good-conditions alerts** (e.g. "mild and overcast tomorrow, a good day to plant out").
- **Only relevant alerts:** sent only when something actually planted is at risk, using each crop's limits from the knowledge base.
- **Actions with each alert:** each action links to a guide and creates a task (e.g. "cover the peppers with fleece tonight").
- **Advance warning and severity:** typically 1–3 days ahead, with watch and warning levels. Urgent alerts (e.g. frost tonight) can override quiet hours.
- **Forecast confidence** is shown, since forecasts more than 3 days out are less reliable.
- **Weather screen:** a 7-day forecast for the plot with gardening notes (good days to work, sow or spray).
- **Follow-up after the event:** after a frost or storm, the app prompts the user to check plants and log damage in the journal.
- **Official warnings:** IPMA (Portugal) in the MVP. Other countries later, via MeteoAlarm or national services (reuse terms to be checked).
- **Backend:** a job fetches the forecast for each plot several times a day, plus official warnings. It compares them with the limits of the crops currently planted, removes duplicate alerts, sends push notifications, creates tasks, and schedules the follow-up after the event.

### 3.13 Plant identification

Point the camera at a plant to learn what it is and what to do about it.

- **Situations covered:** unknown plants on the land, **seedlings** ("my carrot or a weed?"), existing trees and shrubs, and plants at a nursery before buying.
- **Result:** the top possibilities with confidence levels, common names in PT and EN plus the scientific name, a **crop-or-weed verdict**, flags for invasive or toxic plants, and the next step.
- **Context for accuracy:** location, season, and what's planted in that bed.
- **Several photos** (leaf, flower, whole plant), with tips on how to shoot them.
- **One-tap actions:** add as a planting; mark as weed (creates a removal task with the right method); keep (adds the tree to the map as a point of interest).
- **Corrections:** saved, used as context next time, and added to the AI test set.
- **History:** every identification is saved in the journal with its photo.
- **Offline:** photos are queued until the device is online.
- **Limits and safety:**
  - Seedling identification is shown with honest confidence, and the app suggests re-photographing in a week when unsure.
  - **The app never says a wild plant is safe to eat.** Toxicity results are warnings only, with a disclaimer.
  - A specialist plant-ID service could give a second opinion later, with a commercial licence.
- **Backend:** an "identify" task in the AI layer with structured results and context gathering. Results are stored in the activity log, and corrections are kept for the AI test set.

### 3.14 Pest and disease diagnosis

Photograph a plant that looks wrong, find the cause, and get a treatment plan.

- **All causes:** pests, fungal, bacterial and viral diseases, nutrient problems, and **environmental stress** (heat, sunscald, over- or under-watering, frost damage).
- **Context:** crop and growth stage, recent weather, watering schedule, and recent journal entries such as earlier treatments.
- **Follow-up questions** from the AI when it's unsure, before giving a diagnosis.
- **Treatment plan, mildest first:**
  - Prevention and organic methods first.
  - Chemicals only as a last resort, **never naming specific products** (approvals vary by country). The user is pointed to a local agricultural supply shop for approved products, with safety guidance.
- **Treatment tasks plus a check-up** (e.g. re-photograph in 5 days), with a before-and-after comparison.
- **Spread warning** for other beds with susceptible crops. Soil-borne diseases are flagged in the bed's history, so the season planner avoids that crop family there.
- **Warnings before problems appear:** fixed disease-risk rules run on the weather data (e.g. "warm and humid for 3 days, high mildew risk on courgettes"). Linked to weather alerts.
- **Seasonal pest scouting tasks** for the user's crops, region and time of year.
- **Helpful insects:** recognises beneficial insects (e.g. ladybird larvae) so the user doesn't kill them.
- History, corrections and the AI test set, as with plant identification. Offline photos are queued.
- **Limits:** results show confidence. For serious or spreading outbreaks, the app suggests the regional agricultural services (e.g. DRAP Alentejo).
- **Backend:**
  - A "diagnose" task in the AI layer that supports follow-up questions.
  - Disease-risk rules on the weather data.
  - Pest and disease entries in the knowledge base, with organic treatments.
  - Scheduled check-ups.
  - Disease flags in each bed's history, which the season planner reads.

### 3.15 Harvest readiness

Knowing when to pick, and how, to harvest at the best moment.

- **Photo verdict:** a photo, plus planting date and the variety's maturity time, gives one of: not yet (about X days to go), ready soon, ready now, or past its best (pick now, or leave for seed). Each verdict has a confidence level.
- **Advance notice:** the calendar's harvest estimate (accumulated heat) warns when a harvest window is close and asks for a photo check.
- **Signs checklist for each crop (no AI):** e.g. "melon: the stem slips off easily", "garlic: lower leaves turn brown". Crops that can't be judged from a photo (potatoes, carrots, onions, melons) use the checklist plus "dig up one to check" instructions.
- **How to harvest:** technique, best time of day (morning for leafy greens, before the heat), and how to keep plants producing.
- **Weather-aware:** e.g. harvest ripe tomatoes before heavy rain. Linked to weather alerts.
- **One-tap logging:** ready → harvested → quantity in the harvest log.
- **Glut warning** with ideas to preserve or give away.
- **Storage and preserving guides:** how to store each crop, how long it keeps, and simple preserving (drying, freezing, jarring).
- **Later (not in MVP):** saving seeds from the user's own crops.
- **Backend:** a "harvest readiness" task in the AI layer (crop, variety and planting date as context), harvest windows from the calendar, harvest-sign checklists and storage guides in the knowledge base, notifications when a window is approaching, and glut forecasts.

### 3.16 Season planner

Decides which crop goes in which bed, when, and how many, for the coming season and beyond.

- **Inputs:** chosen crops (priority and quantity), beds (size and sun), each bed's history (crop families, disease flags) and calendar windows.
- **Output:** for each bed, the crops, sowing or planting dates, number of plants, and a visual layout inside the bed (rows or grid with spacing).
- **Scan a bed with the camera:** the user takes 2–3 photos along a bed and the AI proposes its layout: rows, row direction, roughly how many plants per row, and the crop when the plants are big enough (with a confidence level). Rows are fitted to the bed's known size, so spacing is approximate. The result is a draft layout that the user confirms or corrects before it's saved. It also compares the planting with the plan (e.g. "planned 36, counted about 30"). It works only once plants are visible (seedlings or planted-out plants), not right after sowing. Offered from "Edit layout" on the bed screen, in the layout editor and as "Scan a bed" in Snap & Ask. One AI vision call per scan (potential premium).
- **AR walk (later):** walking along the bed with the iPhone camera and tapping each row or plant, using Apple's AR to measure real positions. Accurate, no AI cost, works offline; Android needs its own version.
- **Year view of each bed:** a Gantt-style timeline of what occupies each bed, with empty periods highlighted.
- **Follow-on crops** in the same bed (e.g. early potatoes, then autumn cabbages).
- **Cover crops** for beds that would otherwise sit empty, such as broad beans or clover. This is soil care, not soil analysis.
- **Crop rotation:** a 4-group rotation (legumes → brassicas → roots → fruiting crops), with warnings when it's broken, taking disease flags into account.
- **Companion planting with evidence levels:** well supported vs folklore, clearly labelled.
- **Space check:** warns when the crops need more space than is available, and fits the must-haves first.
- **Perennial crops** (asparagus, strawberries, herbs, fruit trees) stay in their beds, and the planner works around them.
- **Drag-and-drop editing**, with rotation, spacing and timing re-checked live.
- **Draft and active plans:** next season is drafted while the current plan runs.
- **Learning from last year:** quantities adjusted from the harvest log and journal notes.
- **AI goals (potential premium):** the AI adjusts the plan for a goal (most harvest, least work, least water) and explains the trade-offs.
- **Confirming a plan** creates planned plantings and tasks, and updates the roadmap.
- **Backend:**
  - A planning engine with fixed rules, possibly using Google OR-Tools (free, runs in .NET) to fit crops into beds.
  - Plan versions (draft and active).
  - Rotation groups and companion pairings with evidence levels in the knowledge base.
  - Each bed's history, built from the activity log.
  - Bed scan: photos go through the AI layer with the bed's size, planned crops and season as context, and come back as a structured draft layout (rows, positions, counts, crop and confidence); nothing is saved until the user confirms.

### 3.17 AI assistant

A gardening expert that knows the user's garden. It answers questions and proposes actions, which are applied only after the user confirms.

- **Ask from anywhere:** a chat screen, plus an **"Ask about this"** button on any bed, plant, task, guide step, alert or diagnosis.
- **Ways to ask:** text, voice (on-phone speech recognition) and photos (passed automatically to identification or diagnosis).
- **Hands-free voice mode:** speech in, spoken answers out using the phone's built-in voice.
- **Context:** plot, zones, crops, plantings, recent journal, weather, tasks and roadmap state, plus relevant knowledge-base content.
- **Answers cite sources** from the knowledge base. It answers in the user's language (PT or EN).
- **Proposed actions:** create or reschedule tasks, add crops, edit the season plan, adjust the watering schedule, log journal entries, add tools to get, open a guide. All need confirmation, are logged, and can be undone.
- **Garden memory the user controls:** facts learned in conversation are saved as notes the user can see, edit and delete.
- **Honesty and safety:** says when it doesn't know; never says a wild plant is safe to eat; never names chemical products; refers serious problems to the regional agricultural services.
- **Offline:** questions are queued and answered when the device is back online, with a notification.
- **Searchable conversation history** and **answer feedback** (thumbs up or down), which feeds the AI test set.
- **Cost control:** a cheaper model for simple questions and a stronger one for complex reasoning (via Foundry), prompt caching for the repeated context, summarised long conversations, and usage limits by tier.
- **Backend:**
  - An assistant endpoint that streams answers.
  - Assistant actions mapped to app commands that create pending proposals.
  - A context builder (garden data plus knowledge-base search).
  - Storage for garden memory and conversations.
  - Usage limits, model routing, and logging of cost and feedback.

### 3.18 Improvement suggestions

A regular review of how the garden is going, with concrete ideas to improve it.

- **Garden report** (weekly by default; fortnightly or monthly as options): what was done and harvested, a weather recap, problems and successes, before-and-after photos from the fixed photo spots, and a preview of next week. Delivered as a notification plus a report screen.
- **Kinds of suggestions:** water (mulch, schedule tweaks), crops (better varieties, new crops to try), pest prevention, layout and paths, infrastructure (windbreak, shade cloth, rain tank), workload (plan less when many tasks are missed).
- **Patterns over time:** insights across weeks and seasons (e.g. a bed that underperforms two seasons in a row).
- **Each suggestion has:** a reason with **evidence** (links to journal entries and photos), and the expected impact and effort.
- **User choices:**
  - Accept: it becomes a proposal, and confirming creates tasks or plan changes.
  - Dismiss with a reason, so it isn't repeated.
  - Snooze.
- **End-of-season review:** a retrospective (yields against expectations, what worked, what to change) that feeds the season planner's draft for next season.
- **Cost control:** statistics are worked out first with fixed rules from the activity log, so there's one AI call per user per review with a compact summary. Without AI, the report still shows the statistics.
- **Backend:**
  - A scheduled review job.
  - Statistics built from the activity log.
  - A "review" task in the AI layer.
  - Suggestions with a status (new, accepted, dismissed, snoozed).
  - Dismissal reasons, stored so suggestions aren't repeated.

### 3.19 App-wide features

- **Home screen ("Today"):** next actions, today's tasks, active weather alerts, the forecast and pending AI proposals on one screen.
- **Navigation:** five tabs (Today, Garden, a central **Snap & Ask** camera button, Plan, Journal). Guides, Tools, Weather, Garden memory and Settings open from the profile picture ("Me"). Sub-screens use a back button labelled with the screen they return to.
- **Snap & Ask:** one camera for every photo feature. A menu picks the mode (identify, diagnose, check harvest, scan a bed, assess a zone, ask the assistant); the camera shows tips and how many photos each mode needs, and a bed chip the app guesses and the user confirms. Photos are queued while offline.
- **Garden tab:** the plot map with zones and their phase, a zone screen (beds and their status, next actions, site assessment summary, recent history) and a bed screen (growing now and planned, layout, rotation, upcoming tasks).
- **First-run setup:** a guided flow: location → draw the plot → what already exists → site assessment → choose crops → preferences. At the end, the roadmap is ready.
- **Settings:** language, units (metric or imperial), notification preferences and quiet hours, morning summary time, the plan-next-week reminder day, the "always own" tools setting, the phone's "Garden" calendar, report frequency, anonymous crash reports, and an **AI usage meter**.
- **Privacy:** GPS data is stripped from photos before they're uploaded or shared, and the plot's exact location is kept private.
- **Error and crash reporting:** crash reports and basic anonymous usage statistics (Application Insights on the backend, Xcode's crash reports on iOS, Android vitals later).
- **Accessibility:** larger text, VoiceOver and TalkBack support, and colour choices that work for colour-blind users, built in from the start.
- **Later (not in MVP):** home screen widgets (today's tasks and alerts), Apple Watch quick logging, Siri shortcuts.

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
   External data: Open-Meteo (weather, climate, elevation) · SoilGrids (soil)
   Identity: Entra External ID (email, Sign in with Apple, Google)
```

### Components
1. **Identity:** Entra External ID, signed in with MSAL on both apps. Multi-user from day one, with every record scoped to a user.
2. **Core API:** plots, zones and beds (PostGIS geometry), plantings, tasks, journal, tools, plans. Built with ASP.NET Core and EF Core, using NetTopologySuite for geometry.
3. **Activity log and roadmap engine:**
   - **Activity log:** an entry is saved for everything that happens (actions done, skipped or done differently, journal notes, photo results, changes of state). Entries are timestamped and never overwritten.
   - **Zone state:** a current-state view of each zone, built from the log. The zone's phase is worked out from it.
   - **Next actions:** a rules layer (agronomy logic and safety limits that are never broken) produces the possible actions and their time windows. An AI layer ranks them, adapts them to deviations, explains why, and estimates time and cost. The result is a short list of next actions for each zone, each with a reason, a time window, a guide link and the tools needed.
   - **When it recalculates:** on relevant events (an action recorded, a photo analyzed, a significant forecast change) and once a day. The rules run every time, the AI only when the change matters, to keep costs down. The latest result is cached on the phone for offline use.
   - **Traceability:** each recommendation records the knowledge-base version and AI model that produced it.
4. **Sync API:** offline-first sync.
   - Clients generate the record IDs (UUIDs).
   - Every record carries a server version number.
   - Deleted records are marked as deleted (soft deletes) rather than removed.
   - Endpoints are `POST /sync/push` and `GET /sync/pull?since=<token>`.
   - Activity log entries are only ever added, never edited, so they sync without conflicts.
   - **Conflicts on editable records are resolved by the user.** When a push carries an outdated version, the server keeps its current version and returns both. The app records a pending conflict and shows both versions side by side. The user keeps one or combines them field by field. Conflicts don't block other work: they appear as a badge on the "Today" screen. Every resolution is logged.
5. **Media:** the API issues short-lived SAS upload URLs, the phone uploads directly to Blob Storage, and a queue triggers thumbnail creation and any AI analysis.
6. **AI layer:** one `IAiService` handles every task: site assessment, identification, diagnosis, harvest readiness, assistant chat (tool use that creates **pending proposals**), plan explanation and the weekly review.
   - It assembles the context for each call: garden, history, weather, and relevant knowledge-base content.
   - Usage is limited per user according to their plan tier.
   - Every request is logged with its cost.
   - The model can be swapped.
7. **Knowledge base:** crops (temperature thresholds, frost tolerance, days to maturity, rotation family, spacing, watering guidance by season), tools, techniques and guides.
   - The **source of truth lives in git** under `content/` as YAML and Markdown, in both PT and EN.
   - A pipeline publishes it to the database and Blob Storage, and builds offline packages.
   - The AI uses it as grounding through **hybrid search**: search by meaning with **OpenAI `text-embedding-3-small`** (via Azure OpenAI / Foundry) stored in pgvector, combined with PostgreSQL keyword search (PT and EN). Embeddings are generated by the content pipeline when content is published, so there's no cost per question beyond embedding the question itself.
   - **Kept current:** each item cites its sources (e.g. FAO, agricultural extension services) and has a "last reviewed" date. A scheduled AI job flags outdated content and proposes updates as pull requests to `content/`. **A person reviews each update before it's published.** Nothing is published automatically from the web.
8. **External data adapters:** Open-Meteo (forecast, historical climate, elevation) and SoilGrids (soil). The results are cached for each plot.
9. **Worker:** queue processing and scheduled jobs (roadmap recalculation, weather alerts, reminders, weekly reviews, content freshness review).
10. **Notifications:** Azure Notification Hubs (free tier), sending to APNs and FCM.
11. **Later:** App Store and Play subscription receipt validation, IoT and sensor ingestion, a content admin interface, and a Python service for raster or ML work.

### Continuous integration and delivery
The API deploys automatically; the mobile apps are released by hand (TestFlight, later Google Play).

- **Branches:** `main` is protected. Every change, planning documents included, goes through a pull request, and **the owner merges every pull request**. No approvals are required while working solo (GitHub doesn't allow approving your own pull request); collaborators' pull requests will need the owner's approval.
- **Required checks on every pull request** (a pull request can't merge if any fails):
  1. **Build:** API build, format check, and a check that the OpenAPI description matches the code (the Swift client is generated from it).
  2. **API unit tests.**
  3. **API integration tests:** against PostgreSQL with PostGIS and pgvector, and Azurite, started as containers in the pipeline. AI calls use a fake provider with canned answers.
  4. **iOS unit tests** and 5. **iOS UI tests** (XCUITest on a simulator, against a fake API). These run **only when the pull request changes the iOS app or the OpenAPI description**; otherwise they report "not needed" and pass, to stay within GitHub's free Mac minutes.
  6. **QA deploy and smoke test.**
  Android checks are added with the Android app (Linux runner, only when `android/` changes).
- **QA: one version per pull request.** Each pull request gets its own Container Apps revision with its own URL (label `pr-<n>`), its own database `qa_pr_<n>` with the schema and sample data, and its own storage folder; the AI uses the fake provider unless switched on. The pipeline comments the URL on the pull request. When the pull request is merged or closed, the revision, database and files are removed. Test builds of the app have a hidden setting to point at a QA URL.
- **Container images** are stored in **GitHub Container Registry** (ghcr.io, private, free at this size) instead of Azure Container Registry; Container Apps pull them with a read-only registry token kept in Key Vault.
- **Prod: deploys when `main` changes** (merging a pull request updates `main`): build the image, run the database migrations, start the new revision, check its health, then move traffic to it. If the health check fails, traffic stays on the old revision.
- **Databases:** prod and QA databases live on the **same PostgreSQL server**, with separate databases and logins, so QA adds no cost.
- **Tests are part of every feature:** each feature's tasks include API unit tests, API integration tests, iOS unit tests and iOS UI tests (Android tests in each Android port), on top of the manual "Test on iPhone" check.

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
| Embeddings (text-embedding-3-small) | Pay per use, a few cents at personal usage |
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

## 6. Releases and sprints

Milestones M0–M7 were replaced by **release tiers and sprints**, based on the owner's priorities in `planning/feature-priorities.xlsx` (the owner's choices, with Claude's suggestion wherever a row was left blank).

- **Release tiers** (GitHub labels): **MVP** → **Good to have** → **Future improvement** (not scheduled).
- **Sprints** (GitHub milestones): a capacity of **100 effort points per sprint, where 1 point = 1 hour** including the owner's testing time. Tasks are ordered by tier, then by phase (foundations → plot → crops and calendar → roadmap → journal and tasks → tools and irrigation → guides → weather → AI photo features → season planner → assistant → release), then filled into sprints in that order. A new sprint starts at the MVP / Good to have boundary.
- **Work items** (GitHub issues): Epic (Feature type + `epic` label) → Feature (PBI) → Task, linked as sub-issues. Tasks carry an area label and their estimate.
- **iOS first:** the MVP is iOS only and ends with a TestFlight release. Android is ported at the start of Good to have, and good-to-have features are ported at the end.
- **Offline sync is Good to have** (owner priority). The MVP works online, but the data model uses client-generated IDs and server versions from the start, so sync can be added without migrations.

The full sprint plan, with hours per sprint and epic, is in **`planning/backlog/BACKLOG.md`**. The task source is the JSON fragments in `planning/backlog/`. `build.py` validates and schedules them, and the **Import backlog** GitHub Actions workflow creates the issues.

---

## 7. Licensing to verify before going commercial

- Satellite map tiles (Apple, Google) may be displayed, but not analyzed by AI or stored.
- Open-Meteo's free API is non-commercial only. It needs a paid plan or an alternative.
- IPMA and MeteoAlarm warnings: check the reuse terms for commercial use.
- SoilGrids is CC-BY, so it needs attribution. Check the API's rate limits.
- Specialist plant-ID APIs (Pl@ntNet, Kindwise): their free tiers are non-commercial.
- Check the availability and pricing of Claude models in Microsoft Foundry.
- Check OpenAI's current terms for commercial use of gpt-image outputs, and Azure OpenAI's content policies.

---

## 8. Open decisions

- None at the moment. New open questions are added here as they come up.
