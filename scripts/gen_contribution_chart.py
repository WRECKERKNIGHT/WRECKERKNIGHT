import json
import os
import time
import urllib.request
import datetime
import pathlib

USER = "WRECKERKNIGHT"
TZ_OFFSET = 5.5
WEEKS = 17  # ~4 months
CELL, GAP, PAD_L, PAD_T, R = 14, 3, 40, 62, 3
DARK = "#161b22"
DIM = "#1e2630"
AMBER = "#F7B733"
CYAN = "#00E5FF"
PINK = "#F700FF"
GREY = "#30363d"


def get(url):
    headers = {"User-Agent": "contrib-chart", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20))


def esc(s):
    return s.replace("&", "&amp;")


def fetch_daily_counts():
    hist = {}
    for page in (1, 2, 3):
        try:
            events = get(f"https://api.github.com/users/{USER}/events/public?per_page=100&page={page}")
        except Exception as e:
            print(f"  events page {page} failed: {e}")
            break
        if not events:
            break
        for ev in events:
            if ev.get("type") != "PushEvent":
                continue
            size = ev.get("payload", {}).get("size", 0) or len(ev.get("payload", {}).get("commits", []))
            ts = datetime.datetime.fromisoformat(ev["created_at"].replace("Z", "+00:00"))
            local = ts + datetime.timedelta(hours=TZ_OFFSET)
            day = local.strftime("%Y-%m-%d")
            hist[day] = hist.get(day, 0) + max(size, 1)
    return hist


def intensity(count):
    if count == 0:
        return DARK, DIM
    if count <= 2:
        return AMBER, "#6b5318"
    if count <= 5:
        return AMBER, "#9d7a1e"
    if count <= 10:
        return "#ffc42e", AMBER
    return CYAN, AMBER


def build_svg(hist):
    now_local = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=TZ_OFFSET)
    end_date = now_local.date()
    start_date = end_date - datetime.timedelta(weeks=WEEKS - 1, days=6)

    # shift start to Sunday
    start_date -= datetime.timedelta(days=start_date.weekday() + 1)

    grid = []
    day_labels = ["", "Mon", "", "Wed", "", "Fri", ""]
    week_labels = set()
    max_count = max(hist.values()) if hist else 1

    y = PAD_T
    for dow in range(7):
        if dow % 2 == 1:
            grid.append(f'  <text x="34" y="{y + R + 4}" font-family="ui-monospace,monospace" font-size="10" fill="{GREY}" text-anchor="end">{day_labels[dow]}</text>')
        x = PAD_L
        for week in range(WEEKS):
            day = start_date + datetime.timedelta(weeks=week, days=dow)
            if day > now_local.date():
                # future cell — skip
                x += CELL + GAP
                continue
            if dow == 6:
                week_labels.add((week, x, day))
            count = hist.get(day.isoformat(), 0)
            fill, stroke = intensity(count)
            opacity = "0.4" if count == 0 else "1"
            anim = ""
            if day == now_local.date():
                anim = f'<animate attributeName="opacity" values="1;0.5;1" dur="2s" repeatCount="indefinite"/>'
            grid.append(f'  <rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{R}" fill="{fill}" stroke="{stroke}" stroke-width="1" opacity="{opacity}">{anim}</rect>')
            x += CELL + GAP
        y += CELL + GAP

    # week labels (first of month)
    for week, x, day in sorted(week_labels):
        if day.day <= 7:
            grid.append(f'  <text x="{x + CELL // 2}" y="{PAD_T - 10}" font-family="ui-monospace,monospace" font-size="10" fill="{GREY}" text-anchor="middle">{day.strftime("%b")}</text>')

    total = sum(hist.values())
    grid_w = PAD_L + WEEKS * (CELL + GAP)
    grid_h = PAD_T + 7 * (CELL + GAP) + 10
    W = grid_w + 30
    H = grid_h + 40

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Contribution heatmap from real commit data">
  <defs>
    <linearGradient id="cbg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0d1117"/>
      <stop offset="100%" stop-color="#12101c"/>
    </linearGradient>
  </defs>

  <rect width="{W}" height="{H}" rx="16" fill="url(#cbg)" stroke="#232134" stroke-width="2"/>

  <text x="34" y="38" font-family="'Courier New',monospace" font-size="20" font-weight="900" letter-spacing="5" fill="{AMBER}">CONTRIBUTION.GRID</text>
  <text x="{W - 14}" y="38" font-family="'Courier New',monospace" font-size="14" fill="#6e7681" text-anchor="end">{esc(now_local.strftime("%d.%m %H:%M IST"))} &#183; {total} events tracked</text>

{chr(10).join(grid)}

  <!-- legend -->
  <g transform="translate({W - 180},{H - 18})">
    <text x="0" y="0" font-family="ui-monospace,monospace" font-size="9.5" fill="#6e7681">less</text>
    <rect x="28" y="-8" width="10" height="10" rx="2" fill="{DIM}" stroke="{GREY}" stroke-width="0.5"/>
    <rect x="42" y="-8" width="10" height="10" rx="2" fill="#6b5318" stroke="{GREY}" stroke-width="0.5"/>
    <rect x="56" y="-8" width="10" height="10" rx="2" fill="#9d7a1e" stroke="{GREY}" stroke-width="0.5"/>
    <rect x="70" y="-8" width="10" height="10" rx="2" fill="{AMBER}" stroke="{GREY}" stroke-width="0.5"/>
    <rect x="84" y="-8" width="10" height="10" rx="2" fill="{CYAN}" stroke="{GREY}" stroke-width="0.5"/>
    <text x="100" y="0" font-family="ui-monospace,monospace" font-size="9.5" fill="#6e7681">more</text>
  </g>
</svg>
'''
    pathlib.Path("assets/contribution-grid.svg").write_text(svg, encoding="utf-8")
    print(f"grid -> {WEEKS} weeks · {total} events · max daily: {max_count}")


try:
    hist = fetch_daily_counts()
    build_svg(hist)
except Exception as e:
    print(f"failed, keeping previous chart: {e}")
