import json
import random
import re
import urllib.request
import datetime
import pathlib

UID = "31y7htruozzrnh2fraukjakcg4ii"
SPOTIFY_URL = ("https://spotify-github-profile.kittinanx.com/api/view"
               f"?uid={UID}&cover_image=false&theme=default&show_offline=true"
               "&background_color=121212&interchange=false&profanity=false&hide_remaster=false")
GH_USER = "WRECKERKNIGHT"

GREEN, PINK, CYAN, AMBER, RED = "#27C93F", "#F700FF", "#00E5FF", "#F7B733", "#FF5C57"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fetch_track():
    req = urllib.request.Request(SPOTIFY_URL, headers={"User-Agent": "bottom-bar"})
    svg = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    artist = re.search(r'class="artist">\s*(.*?)\s*</div>', svg, re.S)
    song = re.search(r'class="song">\s*(.*?)\s*</div>', svg, re.S)
    if 'class="playing"' in svg and artist and song:
        a, s = artist.group(1).strip(), song.group(1).strip()
        combined = f"{a} {s}".lower()
        if "offline" in combined or "not playing" in combined or "not listening" in combined:
            return False, "", ""
        return True, a, s
    return False, "", ""


def fetch_stats():
    def get(url):
        req = urllib.request.Request(url, headers={
            "User-Agent": "bottom-bar", "Accept": "application/vnd.github+json"})
        return json.load(urllib.request.urlopen(req))

    user = get(f"https://api.github.com/users/{GH_USER}")
    repos, page = [], 1
    while True:
        batch = get(f"https://api.github.com/users/{GH_USER}/repos?per_page=100&page={page}")
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return user["public_repos"], sum(r["stargazers_count"] for r in repos), user["followers"]


def marquee_text(text, region_w, char_w=9.6):
    base = f" {text} "
    reps = max(1, int((region_w / (len(base) * char_w)) + 1))
    return base * reps


def eq_bars(x0, n, color):
    out, rng = [], random.Random(7)
    for i in range(n):
        x = x0 + i * 11
        vals = [rng.choice([5, 9, 14, 19, 23]) for _ in range(6)]
        hv = ";".join(map(str, vals))
        yv = ";".join(str(46 - h) for h in vals)
        dur = round(rng.uniform(0.65, 1.15), 2)
        out.append(
            f'<rect x="{x}" y="{46 - vals[0]}" width="5" height="{vals[0]}" fill="{color}">'
            f'<animate attributeName="height" values="{hv}" dur="{dur}s" begin="{-0.09 * i:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="y" values="{yv}" dur="{dur}s" begin="{-0.09 * i:.2f}s" repeatCount="indefinite"/>'
            f"</rect>"
        )
    return "\n      ".join(out)


try:
    playing, artist, song = fetch_track()
except Exception as e:
    print("spotify fetch failed:", e)
    playing, artist, song = False, "", ""

repos, stars, followers = fetch_stats()
now = datetime.datetime.now(datetime.timezone.utc).strftime("%d.%m %H:%M")

W, H = 1440, 56
clip_x, clip_w = 130, 470          # media text scroll region
tray_x = 640                       # tray starts after divider

if playing:
    track = f"NOW PLAYING \u25b8 {artist} \u2014 {song}"
    track_col, eq_col = CYAN, AMBER
else:
    track = f"SPOTIFY.IDLE \u25b8 NOTHING.PLAYING \u25b8 QUEUE.OPEN \u25b8 SYNC {now} UTC"
    track_col, eq_col = AMBER, "#444c56"

mtxt = esc(marquee_text(track, clip_w))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="System tray bar: now playing, online status and repo telemetry">
  <rect width="{W}" height="{H}" fill="#0d1117"/>
  <line x1="0" y1="1" x2="{W}" y2="1" stroke="{PINK}" stroke-opacity="0.55"/>
  <line x1="0" y1="{H - 1}" x2="{W}" y2="{H - 1}" stroke="{CYAN}" stroke-opacity="0.55"/>
  <clipPath id="media"><rect x="{clip_x}" y="0" width="{clip_w}" height="{H}"/></clipPath>

  <!-- MEDIA PLAYER -->
  <g font-family="'Courier New',monospace" clip-path="url(#media)">
      {eq_bars(16, 9, eq_col)}
      <text x="{clip_x + 10}" y="34" font-size="19" font-weight="bold" fill="{track_col}">{mtxt}</text>
      <animateTransform attributeName="transform" type="translate" from="0 0" to="{-clip_w} 0" dur="16s" repeatCount="indefinite"/>
  </g>
  <g font-family="'Courier New',monospace" clip-path="url(#media)">
      <text x="{clip_x + 10 + clip_w}" y="34" font-size="19" font-weight="bold" fill="{track_col}">{mtxt}</text>
      <animateTransform attributeName="transform" type="translate" from="0 0" to="{-clip_w} 0" dur="16s" repeatCount="indefinite"/>
  </g>
  <line x1="{tray_x - 20}" y1="10" x2="{tray_x - 20}" y2="{H - 10}" stroke="#30363d"/>

  <!-- SYSTEM TRAY -->
  <g font-family="'Courier New',monospace" font-size="17" font-weight="bold">
    <circle cx="{tray_x + 22}" cy="28" r="6" fill="{GREEN}">
      <animate attributeName="opacity" values="1;0.35;1" dur="1.3s" repeatCount="indefinite"/>
    </circle>
    <circle cx="{tray_x + 22}" cy="28" r="3" fill="{GREEN}"/>
    <text x="{tray_x + 38}" y="34" fill="{GREEN}">ONLINE</text>

    <line x1="{tray_x + 122}" y1="12" x2="{tray_x + 122}" y2="{H - 12}" stroke="#30363d"/>
    <text x="{tray_x + 142}" fill="{CYAN}">REPOS:{repos}</text>

    <text x="{tray_x + 262}" fill="{AMBER}">&#9733;:{stars}</text>

    <text x="{tray_x + 330}" fill="{PINK}">FOLLOWERS:{followers}</text>

    <line x1="{tray_x + 492}" y1="12" x2="{tray_x + 492}" y2="{H - 12}" stroke="#30363d"/>
    <circle cx="{tray_x + 516}" cy="28" r="5" fill="{RED}">
      <animate attributeName="opacity" values="1;0;1" dur="1s" calcMode="discrete" repeatCount="indefinite"/>
    </circle>
    <text x="{tray_x + 530}" fill="{PINK}">LIVE</text>
    <rect x="{tray_x + 580}" y="18" width="9" height="19" fill="{CYAN}">
      <animate attributeName="opacity" values="1;0;1" dur="0.9s" calcMode="discrete" repeatCount="indefinite"/>
    </rect>

    <text x="{W - 14}" y="34" text-anchor="end" fill="#8d7b94">IST.UTC+05:30</text>
  </g>
</svg>
'''

pathlib.Path("assets/bottom-bar.svg").write_text(svg, encoding="utf-8")
print(f"bar built -> playing={playing} track='{artist} - {song}' repos={repos} stars={stars} followers={followers}")
