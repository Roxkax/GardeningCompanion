# Screen render conventions

Every screen is a standalone HTML file rendered to a PNG of an iPhone (393×852 screen inside a frame).

## Files
- Work folder: the render folder that holds `frame.css` and `shot.js` (the copies here in `design/source/` are the same files).
- Source: `<CODE>-<slug>.html`, e.g. `C2-zone-detail.html`. Output: same name `.png`.
- Render: `NODE_PATH=$(npm root -g) node shot.js <CODE>-<slug>.html <CODE>-<slug>.png`
- After checking the render, copy the PNG to `design/screens/` and the HTML to `design/source/`.

## Page skeleton
- `<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700;800&display=swap" rel="stylesheet">` and `<link rel="stylesheet" href="frame.css">`.
- `.stage > .phone > .screen` containing `.island`, `.status` (copy the 9:41 status bar markup from `A2-find-your-plot.html`), the content, and `.home`.
- Tokens in `frame.css`: `--bg #F5F6F0`, `--card #FFF`, `--line #DCE1D5`, `--text #1F2A20`, `--muted #4E5A4C`, `--green #2D6A3A` (actions), `--green-soft #E3F0E1`, orange `#9A4A0C` / `#FFF1E3` (warnings only), blue `#1E4E7A` / `#E3EDF7`.
- Font: Figtree. Large title 32–34px/800 for tab roots; nav titles 17px/700; section headings 20–21px/800; body 15–17px; meta 13–14px muted.
- Cards: white, 1px `--line` border, radius 16px, padding 14–16px. Touch targets ≥ 44px. Primary button `.btn.primary` (green), secondary `.btn.secondary`.
- Icons: inline stroke SVG (2–2.2 stroke, round caps). **No emoji.**

## Screen types
- **Setup screens (A2–A8):** back circle button + "Set up your garden · Step N of 7" + 7-segment `.progress`. Map screens use a full-bleed drawn satellite SVG with a bottom sheet (see A3/A4).
- **Tab root screens (B1, C1, E1, F1 …):** large title, avatar button "D" (green circle, 44px) top right that opens G1 Me, and the **tab bar** at the bottom: Today · Garden · centre camera button (Snap & Ask, 58px green circle raised) · Plan · Journal, with the active tab in green. Copy the tab bar from `B1-today.html` once it exists, else from the canvas Today mockup.
- **Detail screens:** nav bar with back chevron (44px) **labelled with the screen it returns to** (e.g. "‹ Today"), centred title 17px/700–800 with an optional small subtitle, optional right action. **No large title and no avatar** on drill-downs; those belong only to the five tab roots. No tab bar on full-screen flows (camera, editors, guide doing mode); keep it on drill-downs inside a tab.
- Scrolling screens may continue below the fold: show the top of the screen, content can be cut by the tab bar like a real scroll.

## Shared sample data (keep consistent)
- User initial **D**. Date **Tuesday 20 October**. Plot near **Évora, Alentejo**, 6,480 m² (0.65 ha).
- **Zone A** · Vegetables · 2,140 m² · full sun · green `#2D6A3A` · has the well. Beds A1–A4 (1.2 × 6 m).
- **Zone B** · To clear first · 1,860 m² · full sun · blue `#2F6FB0` · brambles along the fence.
- **Zone C** · Olive trees · 2,480 m² · part shade · brown `#7A4F1E`.
- Weather: 24° / 12° sunny, no rain for 6 days, rain Saturday, **frost risk Thursday night**.
- Chosen crops: broad beans, peas, garlic, short-day onions, lettuce, cabbage; spring: tomatoes, peppers, courgettes.
- Tools: "always own" is on; missing: brush cutter. Owned: spade, rake, hoe, wheelbarrow, hose, gloves.
- AI suggestions are proposals the user confirms. Never name chemical products; never say a wild plant is safe to eat.
- English UI copy, plain and short.

## Scrolling screens
For screens taller than one phone screen, also render a full-length version (`<CODE>-<slug>-full.html/.png`): same file with `.stage`, `.phone` and `.screen` heights increased so the whole scroll is visible, rendered with a matching viewport height (e.g. `node shot.js X-full.html X-full.png 520 1460`). Send the full version for review.
