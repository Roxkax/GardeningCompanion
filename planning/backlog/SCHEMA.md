# Backlog fragment schema

Each worker writes one JSON file in `planning/backlog/` named `<fragment>.json`, holding a list of epics:

```json
[
  {
    "key": "E05",                      // epic key, given in the assignment
    "title": "Planting calendar",
    "summary": "One paragraph: what this epic delivers (plain English).",
    "plan_ref": "PLAN.md §3.5",
    "features": [
      {
        "key": "3.5.1",                // row ID from priorities-final.json, or "X.<epic>.<n>" for extra features
        "title": "Climate-based windows",
        "priority": "MVP",             // exactly "MVP" | "Good to have" | "Future improvement"
        "seq": 3,                      // sequencing phase (see table below); ignored for Future improvement
        "story": "As a beginner gardener, I want … so that …",
        "acceptance": ["Given/when/then or checklist item", "..."],   // 3–6 items
        "depends_on": ["0.5", "X.E00.3"],   // feature keys that must be done first (may be empty)
        "tasks": [                     // [] for Future improvement features
          {
            "title": "Imperative, specific, ≤ 80 chars",
            "area": "backend",         // backend | ios | android | content | infra | design | testing
            "hours": 4,                // integer 1–8, INCLUDES the owner's time to test it
            "description": "1–3 sentences: what to do, and the definition of done."
          }
        ]
      }
    ]
  }
]
```

## Rules
- Every feature row from `priorities-final.json` in your epics must appear exactly once, with its priority unchanged.
- **Future improvement** features: `tasks: []`, `seq: 99`.
- **MVP and Good to have** features: break into **as many small tasks as make sense** (typically 3–8), each 1–8 hours.
  - Typical split: backend data model/migration, backend API/logic, backend tests, iOS screen(s), iOS integration, content authoring, and a final **testing** task "Test <feature> on iPhone" (on the plot where relevant).
  - Hours include the owner's testing time. The owner is an experienced developer working solo with AI help, but new to Swift-level detail is not assumed — estimate realistically.
  - **iOS only.** Android work lives only in the Android epic (E01).
- Don't duplicate shared platform work that belongs to Foundations (E00): API skeleton, auth, AI layer core, media/photo upload service, push notification infrastructure, weather data service, knowledge base pipeline, crop/tool catalog schema. Reference it in `depends_on` instead.
- English, plain language. No model names except Claude/gpt-image/text-embedding-3-small where needed.

## Sequencing phases (`seq`)
| seq | Phase |
|---|---|
| 1 | Platform foundations: repo, CI, infra, API skeleton, auth, data model, i18n, activity log |
| 2 | Plot mapping (map, zones, beds, points of interest, layout) |
| 3 | Knowledge base content, crop catalog, choosing crops, planting calendar |
| 4 | Roadmap engine (rules), first-run setup, "Today" screen |
| 5 | Journal and tasks |
| 6 | Tools and irrigation |
| 7 | Guides |
| 8 | Weather alerts |
| 9 | AI layer, site assessment, plant ID, pest and disease, harvest readiness |
| 10 | Season planner |
| 11 | AI assistant |
| 12 | App-wide polish, privacy, accessibility, TestFlight release of the MVP |
| 20–39 | Good to have: use 20 + the epic's position (e.g. Android = 20, others 21–39 in epic order) |
| 99 | Future improvement |

Good-to-have features use seq 20–39; MVP features use 1–12.
