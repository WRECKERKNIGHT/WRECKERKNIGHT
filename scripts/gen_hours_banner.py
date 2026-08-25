import json
import os
import time
import urllib.request
import datetime
import pathlib

USER = "WRECKERKNIGHT"
HOURS_PER_COMMIT = 1.25

PINK, CYAN, GOLD, GRAY = "#F700FF", "#00E5FF", "#F7B733", "#9aa4ad"


def get(url):
    headers = {
        "User-Agent": "hours-banner",
        "Accept": "application/vnd.github+json",
    }
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    return json.load(urllib.request.urlopen(req))


def esc(s):
    return s.replace("&", "&amp;")


def fmt(n):
    return f"{n:,}"


def fetch_commits():
    return get(f"https://api.github.com/search/commits?q=author:{USER}+is:public").get("total_count", 0)


def odometer_frames(x, y, value, fill, t_start, step=0.22, font_size=118):
    v = value
    fracs = [0.0, 0.15, 0.32, 0.52, 0.72, 0.88, 1.0]
    vals, seen = [], set()
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
        end_attr = ' fill="freeze"' if is_last else ""
        anims = (
            f'<animate attributeName="opacity" begin="cycle.begin+{begin:.2f}s" dur="0.01s" '
            f'values="0;1" calcMode="discrete"{end_attr} repeatCount="1"/>'
        )
        if not is_last:
            nxt = begin + step
            anims += (
                f'<animate attributeName="opacity" begin="cycle.begin+{nxt:.2f}s" dur="0.01s" '
                f'values="1;0" calcMode="discrete" repeatCount="1"/>'
            )
        out.append(
            f'      <text x="{x}" y="{y}" font-family="\'Courier New\',monospace" font-size="{font_size}" '
            f'font-weight="900" fill="{fill}" opacity="0" filter="url(#glow2)">{fmt(n)}{anims}</text>'
        )
    return "\n".join(out), t_start + step * len(vals)


def build(hours, commits, sync):
    odo, _ = odometer_frames(64, 172, hours, "url(#hourgrad)", 0.35)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="236" viewBox="0 0 1440 236" role="img" aria-label="Hours spent coding">
  <defs>
    <linearGradient id="hbg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#160f1d"/>
      <stop offset="100%" stop-color="#0d1117"/>
    </linearGradient>
    <linearGradient id="hourgrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#F700FF"/>
      <stop offset="55%" stop-color="#C77DFF"/>
      <stop offset="100%" stop-color="#00E5FF"/>
    </linearGradient>
    <filter id="glow2" x="-25%" y="-25%" width="150%" height="150%">
      <feGaussianBlur stdDeviation="6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- hidden master clock -->
  <rect width="0" height="0" fill="none">
    <animate id="cycle" attributeName="x" values="0;0" dur="9s" repeatCount="indefinite"/>
  </rect>

  <rect x="4" y="4" width="1432" height="228" rx="26" fill="url(#hbg)" stroke="#232134" stroke-width="2"/>
  <line x1="4" y1="6" x2="1436" y2="6" stroke="{PINK}" stroke-opacity="0.65"/>
  <line x1="4" y1="230" x2="1436" y2="230" stroke="{CYAN}" stroke-opacity="0.65"/>

  <!-- scanning beam -->
  <rect x="4" y="8" width="1432" height="34" fill="#ffffff" opacity="0">
    <animate attributeName="y" values="8;196;8" dur="8s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.05;0.05" dur="8s" repeatCount="indefinite"/>
  </rect>

  <!-- corner brackets -->
  <path d="M28 34 h22 M28 34 v22" stroke="{PINK}" stroke-width="3" fill="none"/>
  <path d="M1412 34 h-22 M1412 34 v22" stroke="{CYAN}" stroke-width="3" fill="none"/>
  <path d="M28 202 h22 M28 202 v-22" stroke="{CYAN}" stroke-width="3" fill="none"/>
  <path d="M1412 202 h-22 M1412 202 v-22" stroke="{PINK}" stroke-width="3" fill="none"/>

  <text x="64" y="66" font-family="'Courier New',monospace" font-size="21" font-weight="bold" letter-spacing="8" fill="{GOLD}">HOURS.SPENT.CODING</text>
  <circle cx="392" cy="59" r="6" fill="{PINK}">
    <animate attributeName="opacity" values="1;0.15;1" dur="0.85s" calcMode="discrete" repeatCount="indefinite"/>
  </circle>

{odo}

  <!-- context column -->
  <g font-family="'Courier New',monospace" font-weight="bold" text-anchor="end">
    <text x="1396" y="92" font-size="20" fill="{GRAY}">FROM <tspan fill="{CYAN}">{fmt(commits)}</tspan> SHIPPED COMMITS</text>
    <text x="1396" y="126" font-size="20" fill="{GRAY}">FORMULA <tspan fill="{GOLD}">&#8776;1.25H</tspan> PER COMMIT</text>
    <text x="1396" y="160" font-size="17" fill="#6e7681">LIVE.SYNC {esc(sync)} UTC
      <animate attributeName="opacity" values="1;0.45;1" dur="2.4s" repeatCount="indefinite"/>
    </text>
  </g>

  <line x1="1020" y1="52" x2="1020" y2="188" stroke="#30363d"/>

  <text x="64" y="216" font-family="'Courier New',monospace" font-size="12.5" fill="#6e7681">* derived from real commit volume on public repos &#8212; not wall-clock tracking &#183; refreshed every 30 minutes</text>
</svg>
'''
    pathlib.Path("assets/hours-banner.svg").write_text(svg, encoding="utf-8")
    print(f"banner -> {fmt(hours)}+ hours from {commits} commits")


commits = None
for attempt in range(3):
    try:
        commits = fetch_commits()
        break
    except Exception as e:
        print(f"commit fetch attempt {attempt + 1} failed: {e}")
        time.sleep(6)

if commits is None:
    print("all attempts failed - keeping previous banner")
else:
    build(int(commits * HOURS_PER_COMMIT), commits,
          datetime.datetime.now(datetime.timezone.utc).strftime("%d.%m %H:%M"))
