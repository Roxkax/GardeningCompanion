"""Build B2-B7 screen HTML from the shared B1 parts."""
import sys
sys.path.insert(0, '.')
from _parts import HEAD, STATUS, TAB

TAB_ON_TODAY = TAB  # Today already active in B1's tab bar

EXTRA = """
  .nav { display: flex; align-items: center; gap: 8px; height: 48px; }
  .back { width: 44px; height: 44px; border-radius: 999px; display: flex; align-items: center; justify-content: center; margin-left: -10px; }
  .ntitle { flex: 1; text-align: center; font-size: 17px; font-weight: 700; }
  .nright { width: 44px; display: flex; justify-content: flex-end; font-size: 16px; font-weight: 700; color: var(--green); }
  .seg { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); background: #E6E9E0; border-radius: 12px; padding: 3px; }
  .seg span { height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 10px; font-size: 14.5px; font-weight: 600; color: var(--muted); }
  .seg span.on { background: #fff; color: var(--text); font-weight: 800; box-shadow: 0 1px 3px rgba(0,0,0,.12); }
  .day { font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); margin: 2px 2px -6px; }
  .list { background: #fff; border: 1px solid var(--line); border-radius: 16px; overflow: hidden; }
  .item { display: flex; gap: 12px; align-items: center; padding: 11px 14px; border-bottom: 1px solid #EEF0EA; min-height: 58px; }
  .item:last-child { border-bottom: none; }
  .box { width: 24px; height: 24px; border-radius: 7px; border: 2px solid #A9B2A3; flex: none; display: flex; align-items: center; justify-content: center; }
  .box.done { background: var(--green); border-color: var(--green); }
  .it { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px; }
  .it b { font-size: 15.5px; font-weight: 700; }
  .it span { font-size: 13px; color: var(--muted); font-weight: 600; }
  .zc { font-size: 11.5px; font-weight: 800; padding: 2px 7px; border-radius: 6px; }
  .za { background: var(--green-soft); color: var(--green-ink); }
  .zb { background: var(--blue-soft); color: var(--blue-ink); }
  .zcc { background: #F1E7DA; color: #6A4317; }
  .row { display: flex; align-items: center; gap: 10px; }
  .label { font-size: 13px; font-weight: 800; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }
  .kv { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
  .kv div { background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 10px 12px; }
  .kv b { display: block; font-size: 15.5px; font-weight: 800; }
  .kv span { font-size: 12.5px; color: var(--muted); font-weight: 600; }
  .bottom { position: absolute; left: 0; right: 0; bottom: 0; z-index: 30; background: rgba(245,246,240,.97); border-top: 1px solid var(--line); padding: 12px 18px 34px; display: flex; flex-direction: column; gap: 10px; }
"""

CHECK = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5 9-10"/></svg>'
BACK = '<div class="back"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#1F2A20" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 5l-7 7 7 7"/></svg></div>'
CHEV = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#4E5A4C" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>'
CLOCK = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/></svg>'


def page(title, extra_css, body, tab=False):
    html = HEAD.replace('<title>B1 Today</title>', f'<title>{title}</title>') + EXTRA + extra_css + "</style>\n</head>\n<body>\n<div class=\"stage\"><div class=\"phone\"><div class=\"screen\">\n  <div class=\"island\"></div>\n" + STATUS + body
    if tab:
        html += TAB_ON_TODAY
    html += '  <div class="home"></div>\n</div></div></div>\n</body>\n</html>\n'
    return html


def task(title, meta, zone, done=False):
    zcls = {'A': 'za', 'B': 'zb', 'C': 'zcc'}[zone]
    box = f'<div class="box done">{CHECK}</div>' if done else '<div class="box"></div>'
    style = ' style="color: #6B7468; text-decoration: line-through"' if done else ''
    return (f'<div class="item">{box}<div class="it"><b{style}>{title}</b>'
            f'<span class="row" style="gap: 6px"><span class="zc {zcls}">Zone {zone}</span>{meta}</span></div></div>')


# ---------------- B2 Tasks ----------------
b2 = f"""
  <div class="content" style="gap: 14px">
    <div class="head">
      <div><div class="date">20 – 26 October</div><h1>Tasks</h1></div>
      <div class="avatar">D</div>
    </div>
    <div class="seg"><span>Today</span><span class="on">This week</span><span>By zone</span></div>
    <div class="card" style="display: flex; align-items: center; gap: 12px; padding: 12px 14px">
      <div style="width: 40px; height: 40px; border-radius: 12px; background: var(--green-soft); display: flex; align-items: center; justify-content: center"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2D6A3A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4M8 14h3"/></svg></div>
      <div style="flex: 1"><div style="font-size: 16px; font-weight: 700">Weekend planner</div><div style="font-size: 13.5px; color: var(--muted)">Tell us your hours, we pick the tasks</div></div>
      {CHEV}
    </div>
    <div class="row" style="justify-content: space-between"><span style="font-size: 15px; font-weight: 700">9 tasks · about 11 h</span><span class="link">Filter</span></div>
    <div class="day">Today · Tue 20</div>
    <div class="list">
      {task('Water Zone A beds', 'Drip sector 1 · 30 min', 'A', True)}
      {task('Sow broad beans in bed A2', '45 min · guide', 'A')}
      {task('Check cabbages for caterpillars', '10 min', 'A')}
    </div>
    <div class="day">Wednesday 21</div>
    <div class="list">
      {task('Sow lettuce in bed A3', '30 min · before frost', 'A')}
      {task('Mulch around young cabbages', '1 h · straw', 'A')}
    </div>
    <div class="day">Saturday 24</div>
    <div class="list">
      {task('Cut back brambles along the fence', '3 h · brush cutter missing', 'B')}
    </div>
  </div>
"""

# ---------------- B3 Task detail ----------------
b3 = f"""
  <div class="content" style="gap: 12px; bottom: 150px">
    <div class="nav">{BACK}<div class="ntitle">Task</div><div class="nright"><svg width="22" height="22" viewBox="0 0 24 24" fill="#1F2A20"><circle cx="5" cy="12" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="19" cy="12" r="2"/></svg></div></div>
    <div style="display: flex; flex-direction: column; gap: 8px">
      <div class="row" style="gap: 8px"><span class="chip" style="background: var(--blue-soft); color: var(--blue-ink)">Zone B · Clear land</span><span class="meta">From your roadmap</span></div>
      <h1 style="font-size: 25px; line-height: 1.15">Cut back brambles along the fence</h1>
    </div>
    <div class="kv">
      <div><b>Sat 24 Oct</b><span>Planned day</span></div>
      <div><b>About 3 h</b><span>Your estimate</span></div>
      <div><b>Medium</b><span>Effort</span></div>
    </div>
    <div class="card" style="display: flex; flex-direction: column; gap: 6px">
      <div class="label">Why now</div>
      <div style="font-size: 15px; line-height: 1.5">Cutting brambles before the winter rains makes it easier to dig out their roots in November, so Zone B is ready for spring.</div>
    </div>
    <div style="display: flex; flex-direction: column; gap: 8px">
      <div class="label">Tools needed</div>
      <div class="list">
        <div class="item" style="min-height: 52px"><div style="width: 38px; height: 38px; border-radius: 10px; background: #FFF1E3; display: flex; align-items: center; justify-content: center"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#9A4A0C" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l9.5 17h-19z"/><path d="M12 10v4M12 17.5v.01"/></svg></div><div class="it"><b>Brush cutter</b><span style="color: #9A4A0C">You don’t have this yet</span></div><span style="font-size: 14px; font-weight: 700; color: var(--green)">Add to tools to get</span></div>
        <div class="item" style="min-height: 52px"><div style="width: 38px; height: 38px; border-radius: 10px; background: var(--green-soft); display: flex; align-items: center; justify-content: center"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2D6A3A" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5 9-10"/></svg></div><div class="it"><b>Thick gloves</b><span>You have these</span></div></div>
      </div>
    </div>
    <div class="card" style="display: flex; align-items: center; gap: 12px">
      <div style="width: 44px; height: 44px; border-radius: 12px; background: var(--green-soft); display: flex; align-items: center; justify-content: center"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2D6A3A" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z"/><path d="M4 20.5A2.5 2.5 0 0 0 6.5 23H20v-5"/></svg></div>
      <div style="flex: 1"><div style="font-size: 16px; font-weight: 700">Guide: clearing brambles</div><div style="font-size: 13.5px; color: var(--muted)">6 steps · safety tips included</div></div>
      {CHEV}
    </div>
  </div>
  <div class="bottom">
    <div class="btn primary">Mark as done</div>
    <div class="row" style="gap: 10px"><div class="btn secondary" style="flex: 1; height: 46px; font-size: 15.5px">Skipped</div><div class="btn secondary" style="flex: 1; height: 46px; font-size: 15.5px">Couldn’t do it</div></div>
  </div>
"""

# ---------------- B4 Weekend planner ----------------
def plan_row(title, zone, hours, why):
    zcls = {'A': 'za', 'B': 'zb', 'C': 'zcc'}[zone]
    return (f'<div class="item" style="align-items: flex-start"><div class="box done" style="margin-top: 2px">{CHECK}</div><div class="it"><b>{title}</b>'
            f'<span class="row" style="gap: 6px"><span class="zc {zcls}">Zone {zone}</span>{hours}</span>'
            f'<span style="font-weight: 500; line-height: 1.4">{why}</span></div></div>')

b4 = f"""
  <div class="content" style="gap: 14px; bottom: 120px">
    <div class="nav">{BACK}<div class="ntitle">Weekend planner</div><div class="nright"></div></div>
    <div class="card" style="display: flex; flex-direction: column; gap: 12px">
      <div style="font-size: 16px; font-weight: 700">How much time do you have?</div>
      <div class="row" style="justify-content: space-between">
        <span style="font-size: 15px; font-weight: 600; color: var(--muted)">Saturday 24</span>
        <div class="row" style="gap: 14px"><span class="stepbtn">−</span><b style="font-size: 20px; width: 44px; text-align: center">3 h</b><span class="stepbtn">+</span></div>
      </div>
      <div class="row" style="justify-content: space-between">
        <span style="font-size: 15px; font-weight: 600; color: var(--muted)">Sunday 25</span>
        <div class="row" style="gap: 14px"><span class="stepbtn">−</span><b style="font-size: 20px; width: 44px; text-align: center">3 h</b><span class="stepbtn">+</span></div>
      </div>
    </div>
    <div class="row" style="justify-content: space-between"><h2>Suggested for you</h2><span style="font-size: 15px; font-weight: 800; color: var(--green)">5 h 45 of 6 h</span></div>
    <div class="list">
      {plan_row('Spread compost on beds A1–A3', 'A', '2 h · Saturday morning', 'Best before 15 Nov; the afternoon rain helps it settle.')}
      {plan_row('Sow broad beans in bed A2', 'A', '45 min · Saturday morning', 'Ideal sowing window closes next week.')}
      {plan_row('Cut back brambles along the fence', 'B', '3 h · Sunday', 'Must happen this month, and Sunday is dry and cool.')}
    </div>
    <div style="font-size: 14px; color: var(--muted); line-height: 1.45; padding: 0 2px">Left out: “Mulch around cabbages” (1 h). It fits next week. Tap a task to swap it.</div>
  </div>
  <div class="bottom" style="padding-bottom: 34px">
    <div class="btn primary">Add to my weekend</div>
  </div>
"""
b4_css = """
  .stepbtn { width: 40px; height: 40px; border-radius: 12px; background: #EEF0EA; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: 700; color: var(--text); }
"""

# ---------------- B5 Weather alert ----------------
b5 = f"""
  <div class="content" style="gap: 14px; bottom: 120px">
    <div class="nav">{BACK}<div class="ntitle">Weather alert</div><div class="nright"></div></div>
    <div style="background: var(--orange-soft); border: 1px solid #F3C99A; border-radius: 18px; padding: 16px; display: flex; flex-direction: column; gap: 10px">
      <div class="row" style="gap: 8px"><span class="chip" style="background: #9A4A0C; color: #fff">Warning</span><span style="font-size: 13.5px; font-weight: 700; color: #7A3A08">Thursday night · 22–23 Oct</span></div>
      <div style="font-size: 25px; font-weight: 800; line-height: 1.15; color: #5A2A06">Frost possible on Thursday night</div>
      <div class="row" style="gap: 18px; color: #5C3A1A">
        <div><div style="font-size: 26px; font-weight: 800">0 °C</div><div style="font-size: 12.5px; font-weight: 700">Lowest, around 5 am</div></div>
        <div><div style="font-size: 26px; font-weight: 800">70%</div><div style="font-size: 12.5px; font-weight: 700">Forecast confidence</div></div>
      </div>
    </div>
    <div style="display: flex; flex-direction: column; gap: 8px">
      <div class="label">At risk in your garden</div>
      <div class="list">
        <div class="item"><div style="width: 40px; height: 40px; border-radius: 10px; background: var(--green-soft); display: flex; align-items: center; justify-content: center"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#2D6A3A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21V11"/><path d="M12 11C12 7 9 5 5 5c0 4 3 6 7 6zM12 13c0-4 3-6 7-6 0 4-3 6-7 6z"/></svg></div><div class="it"><b>Lettuce seedlings</b><span class="row" style="gap: 6px"><span class="zc za">Zone A</span>Bed A3 · planted 8 days ago</span></div></div>
        <div class="item"><div style="width: 40px; height: 40px; border-radius: 10px; background: #EEF0EA; display: flex; align-items: center; justify-content: center"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4E5A4C" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5 9-10"/></svg></div><div class="it"><b>Cabbages and broad beans</b><span>Frost-hardy · no action needed</span></div></div>
      </div>
    </div>
    <div style="display: flex; flex-direction: column; gap: 8px">
      <div class="label">What to do</div>
      <div class="list">
        <div class="item" style="align-items: flex-start"><div class="box done" style="margin-top: 2px">{CHECK}</div><div class="it"><b>Cover bed A3 with frost fleece</b><span>Thursday before sunset · 15 min · guide</span></div></div>
        <div class="item" style="align-items: flex-start"><div class="box done" style="margin-top: 2px">{CHECK}</div><div class="it"><b>Water bed A3 on Thursday morning</b><span>Moist soil holds heat better · 10 min</span></div></div>
      </div>
    </div>
    <div class="row" style="gap: 8px; font-size: 13px; color: var(--muted); padding: 0 2px"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4E5A4C" stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.01"/></svg>IPMA has a yellow cold warning for Évora district.</div>
  </div>
  <div class="bottom">
    <div class="btn primary">Add 2 tasks</div>
  </div>
"""

# ---------------- B6 AI proposal ----------------
b6 = f"""
  <div class="content" style="gap: 14px; bottom: 170px">
    <div class="nav">{BACK}<div class="ntitle">Suggested change</div><div class="nright"></div></div>
    <div class="row" style="gap: 12px">
      <div style="width: 44px; height: 44px; border-radius: 14px; background: var(--green-soft); display: flex; align-items: center; justify-content: center"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2D6A3A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l1.8 4.7L18.5 9l-4.7 1.8L12 15.5l-1.8-4.7L5.5 9l4.7-1.3z"/><path d="M18 15l.8 2.2L21 18l-2.2.8L18 21l-.8-2.2L15 18l2.2-.8z"/></svg></div>
      <div><div style="font-size: 13px; font-weight: 800; color: var(--green); text-transform: uppercase; letter-spacing: .06em">From the assistant</div><div style="font-size: 21px; font-weight: 800; line-height: 1.2">Move lettuce sowing to next week</div></div>
    </div>
    <div class="card" style="display: flex; flex-direction: column; gap: 6px">
      <div class="label">Why</div>
      <div style="font-size: 15px; line-height: 1.5">Frost is possible on Thursday night. Seeds sown on Wednesday would sprout into it. Next Monday is mild for the following 10 days.</div>
    </div>
    <div style="display: flex; flex-direction: column; gap: 8px">
      <div class="label">What changes</div>
      <div class="list">
        <div style="padding: 12px 14px; display: flex; flex-direction: column; gap: 10px">
          <div style="font-size: 15.5px; font-weight: 700">Sow lettuce in bed A3</div>
          <div class="row" style="gap: 10px">
            <div style="flex: 1; background: #F6EDED; border-radius: 12px; padding: 10px 12px"><div style="font-size: 12px; font-weight: 800; color: #8A2E2E; text-transform: uppercase; letter-spacing: .05em">Before</div><div style="font-size: 16px; font-weight: 700; text-decoration: line-through; color: #6B4A4A">Wed 21 Oct</div></div>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4E5A4C" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
            <div style="flex: 1; background: var(--green-soft); border-radius: 12px; padding: 10px 12px"><div style="font-size: 12px; font-weight: 800; color: var(--green-ink); text-transform: uppercase; letter-spacing: .05em">After</div><div style="font-size: 16px; font-weight: 700">Mon 26 Oct</div></div>
          </div>
        </div>
        <div class="item" style="min-height: 48px; border-top: 1px solid #EEF0EA"><div class="it"><span>Also updated: watering task for bed A3 starts Mon 26</span></div></div>
      </div>
    </div>
    <div style="font-size: 13px; color: var(--muted); padding: 0 2px">Source: crop guide “Lettuce” · minimum soil temperature for sowing</div>
  </div>
  <div class="bottom">
    <div class="btn primary">Confirm change</div>
    <div class="btn secondary">Keep as it is</div>
    <div style="text-align: center; font-size: 13px; color: var(--muted)">You can undo this later from the journal.</div>
  </div>
"""

# ---------------- B7 Sync conflict ----------------
def field(name, a, b, pick):
    on = 'border: 2px solid var(--green); background: #F4FAF3'
    off = 'border: 1px solid var(--line); background: #fff'
    sa, sb = (on, off) if pick == 'a' else (off, on)
    return f"""
      <div style="display: flex; flex-direction: column; gap: 6px">
        <div class="label" style="font-size: 12px">{name}</div>
        <div class="row" style="gap: 8px">
          <div style="flex: 1; {sa}; border-radius: 12px; padding: 10px 12px; font-size: 15px; font-weight: 600">{a}</div>
          <div style="flex: 1; {sb}; border-radius: 12px; padding: 10px 12px; font-size: 15px; font-weight: 600">{b}</div>
        </div>
      </div>"""

b7 = f"""
  <div class="content" style="gap: 14px; bottom: 120px">
    <div class="nav">{BACK}<div class="ntitle">Two versions</div><div class="nright"></div></div>
    <div><h1 style="font-size: 25px; line-height: 1.2">This task was changed on two devices</h1>
      <div style="font-size: 15px; color: var(--muted); line-height: 1.45; margin-top: 6px">Tap the value to keep for each field. Nothing is lost: both versions stay in the history.</div></div>
    <div class="row" style="gap: 8px">
      <div style="flex: 1; font-size: 13.5px; font-weight: 800; display: flex; gap: 6px; align-items: center"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1F2A20" stroke-width="2.2"><rect x="6" y="2.5" width="12" height="19" rx="3"/></svg>This iPhone · 9:12</div>
      <div style="flex: 1; font-size: 13.5px; font-weight: 800; display: flex; gap: 6px; align-items: center"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#1F2A20" stroke-width="2.2"><rect x="3" y="3.5" width="18" height="14" rx="2"/><path d="M9 21h6"/></svg>iPad · 8:47</div>
    </div>
    {field('Title', 'Sow broad beans in A2', 'Sow broad beans in A2 and A4', 'b')}
    {field('Date', 'Sat 24 Oct', 'Sun 25 Oct', 'a')}
    {field('Time', '45 min', '1 h 15', 'b')}
    {field('Notes', 'Soak seeds overnight', '—', 'a')}
    <div class="row" style="gap: 8px; font-size: 13px; color: var(--muted)"><span class="chip" style="background: #ECEDE8; color: #4E5A4C">Later</span>Only appears when offline sync is added.</div>
  </div>
  <div class="bottom">
    <div class="btn primary">Save combined version</div>
  </div>
"""

pages = {
    'B2-tasks': ('B2 Tasks', '', b2, True),
    'B3-task-detail': ('B3 Task', '', b3, False),
    'B4-weekend-planner': ('B4 Weekend planner', b4_css, b4, False),
    'B5-weather-alert': ('B5 Weather alert', '', b5, False),
    'B6-ai-proposal': ('B6 Suggested change', '', b6, False),
    'B7-sync-conflict': ('B7 Two versions', '', b7, False),
}
only = sys.argv[1:]
for name, (title, css, body, tab) in pages.items():
    if only and name not in only:
        continue
    open(f'{name}.html', 'w').write(page(title, css, body, tab))
    print('wrote', name)
