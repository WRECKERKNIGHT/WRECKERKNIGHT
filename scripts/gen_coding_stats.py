import json
import os
import time
import urllib.request
import datetime
import pathlib

USER = "WRECKERKNIGHT"

PINK, CYAN, GOLD, PURPLE, GRAY = "#F700FF", "#00E5FF", "#F7B733", "#B392F0", "#9aa4ad"


def get(url, retries=3):
    headers = {
        "User-Agent": "coding-telemetry",
        "Accept": "application/vnd.github+json",
    }
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    last = None
    for attempt in range(retries):
        try:
            return json.load(urllib.request.urlopen(req, timeout=15))
        except Exception as e:
            last = e
            print(f"  attempt {attempt + 1} failed: {e}")
            time.sleep(5 * (attempt + 1))
    raise last


def esc(s):
    return s.replace("&", "&amp;")


def fmt(n):
    return f"{n:,}"


def fetch_stats():
    commits = get(f"https://api.github.com/search/commits?q=author:{USER}+is:public").get("total_count", 0)
    prs = get(f"https://api.github.com/search/issues?q=author:{USER}+type:pr").get("total_count", 0)
    issues = get(f"https://api.github.com/search/issues?q=author:{USER}+type:issue").get("total_count", 0)

    user = get(f"https://api.github.com/users/{USER}")
    created = datetime.datetime.fromisoformat(user["created_at"].replace("Z", "+00:00"))
    days = max(1, (datetime.datetime.now(datetime.timezone.utc) - created).days)

    return commits, prs, issues, days


def odometer_frames(x, y, value, color, t_start, step=0.18):
    v = int(str(value).replace(",", ""))
    fracs = [0.0, 0.15, 0.32, 0.52, 0.72, 0.88, 1.0]
    vals = []
    seen = set()
    for f in fracs:
        n = v if f == 1.0 else int(round(v * f))
        if n not in seen:
            seen.add(n)
            vals.append(n)
    if vals[-1] != v:
        vals.append(v)

    out = []
    for i, n in enumerate(vals):
        begin = t_start + i * step
        is_last = i == len(vals) - 1
        if is_last:
            anims = (
                f'<animate attributeName="opacity" begin="cycle.begin+{begin:.2f}s" dur="0.01s" '
                f'values="0;1" calcMode="discrete" fill="freeze" repeatCount="1"/>'
            )
        else:
            nxt = begin + step
            anims = (
                f'<animate attributeName="opacity" begin="cycle.begin+{begin:.2f}s" dur="0.01s" '
                f'values="0;1" calcMode="discrete" repeatCount="1"/>'
                f'<animate attributeName="opacity" begin="cycle.begin+{nxt:.2f}s" dur="0.01s" '
                f'values="1;0" calcMode="discrete" repeatCount="1"/>'
            )
        out.append(
            f'      <text x="{x}" y="{y}" font-family="\'Courier New\',monospace" font-size="46" '
            f'font-weight="900" fill="{color}" opacity="0" filter="url(#glow)">{fmt(n)}{anims}</text>'
        )
    return "\n".join(out), t_start + step * len(vals)


def build(commits, prs, issues, days):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%d.%m %H:%M")

    cells = [
        (40, "TOTAL.COMMITS.PUSHED", commits, PINK, "counted live &#183; github search api"),
        (400, "PULL.REQUESTS", prs, CYAN, "authored on public repos"),
        (760, "ISSUES.OPENED", issues, PURPLE, "tracked in public repos"),
        (1120, "DAYS.ON.GRID", days, GOLD, "day zero &#8594; now &#183; non-stop"),
    ]

    cell_svgs = []
    t = 0.35
    for x, label, value, color, sub in cells:
        odo, _ = odometer_frames(x, 118, value, color, t)
        cell_svgs.append(f'''
    <!-- {label} -->
    <path d="M{x - 14} 62 h14 M{x - 14} 62 v10" stroke="{color}" stroke-width="2.5" fill="none"/>
    <path d="M{x + 294} 62 h-14 M{x + 294} 62 v10" stroke="{color}" stroke-width="2.5" fill="none"/>
    <text x="{x}" y="56" font-family="'Courier New',monospace" font-size="14" letter-spacing="3" fill="{GRAY}">{esc(label)}</text>
{odo}
    <text x="{x}" y="138" font-family="'Courier New',monospace" font-size="11.5" fill="#6e7681">{sub}</text>''')
        t += 0.45

    cycle_dur = round(t + 3.0, 1)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="176" viewBox="0 0 1440 176" role="img" aria-label="Coding telemetry: real counted numbers rolling up">
  <defs>
    <linearGradient id="ctbg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#12101c"/>
      <stop offset="100%" stop-color="#0d1117"/>
    </linearGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="3.5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- hidden master clock -->
  <rect width="0" height="0" fill="none">
    <animate id="cycle" attributeName="x" values="0;0" dur="{cycle_dur}s" repeatCount="indefinite"/>
  </rect>

  <rect x="4" y="4" width="1432" height="168" rx="20" fill="url(#ctbg)" stroke="#232134" stroke-width="2"/>
  <line x1="4" y1="6" x2="1436" y2="6" stroke="{PINK}" stroke-opacity="0.6"/>
  <line x1="4" y1="170" x2="1436" y2="170" stroke="{CYAN}" stroke-opacity="0.6"/>

  <rect x="4" y="8" width="1432" height="26" fill="url(#ctbg)" opacity="0">
    <animate attributeName="y" values="8;150;8" dur="7s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.25;0.25" dur="7s" repeatCount="indefinite"/>
  </rect>

  <text x="34" y="36" font-family="'Courier New',monospace" font-size="24" font-weight="900" letter-spacing="6" fill="#ffffff" filter="url(#glow)">CODING.TELEMETRY</text>
  <circle cx="310" cy="29" r="6" fill="{PINK}">
    <animate attributeName="opacity" values="1;0.2;1" dur="0.9s" calcMode="discrete" repeatCount="indefinite"/>
  </circle>
  <text x="1406" y="34" font-family="'Courier New',monospace" font-size="14" fill="#6e7681" text-anchor="end">SYNC {esc(now)} UTC</text>

{"".join(cell_svgs)}

  <text x="34" y="163" font-family="'Courier New',monospace" font-size="12.5" fill="#6e7681">&#9679; NOTHING.ESTIMATED &#8212; every number above is counted directly from the github api</text>
</svg>
'''
    pathlib.Path("assets/coding-stats.svg").write_text(svg, encoding="utf-8")
    print(f"stats -> commits={commits} prs={prs} issues={issues} days={days} frames_roll_on_load")


try:
    commits, prs, issues, days = fetch_stats()
    build(commits, prs, issues, days)
except Exception as e:
    print(f"all attempts failed, keeping previous file: {e}")
