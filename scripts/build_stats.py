"""Build assets/stats.svg — a pixel HUD with live GitHub stats.

Runs daily in GitHub Actions (needs GITHUB_TOKEN). Without a token it
writes a placeholder so the README never shows a broken image.
"""
import json
import math
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(__file__))
from pixelfont import text_rects, text_width  # noqa: E402

USER = os.environ.get("GH_USER", "NahwaKakaa")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "stats.svg")

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar { totalContributions }
    }
  }
}
"""


def fetch():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        print("GraphQL errors:", data["errors"], file=sys.stderr)
        return None
    u = data["data"]["user"]
    langs = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [0, e["node"]["color"] or "#8b949e"])
            langs[n][0] += e["size"]
    total = sum(v[0] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]
    return {
        "contrib": u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "commits": u["contributionsCollection"]["totalCommitContributions"],
        "repos": u["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "followers": u["followers"]["totalCount"],
        "langs": [(n, v[1], v[0] * 100 / total) for n, (v) in top],
    }


def px(x, y, s, c, extra=""):
    return f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{c}"{extra}/>'


def icon(rows, color, x, y, s=3):
    out = []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "#":
                out.append(px(x + c * s, y + r * s, s, color))
    return out


ICONS = {
    "fire": ["...#...", "..##...", ".####..", ".#####.", "#######", "#######", ".#####."],
    "pick": [".#####.", "#..#..#", "...#...", "...#...", "...#...", "...#...", "...#..."],
    "chest": ["#######", "#.....#", "###.###", "#.....#", "#.....#", "#######", "......."],
    "star": ["...#...", "..###..", "#######", ".#####.", ".##.##.", "#.....#", "......."],
    "user": ["..###..", "..###..", "..###..", ".#####.", "#######", "#######", "......."],
}


def build(stats):
    W, H = 880, 300
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" shape-rendering="crispEdges">',
         "<style>.grow{animation:grow 1.6s steps(12) both}@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
         ".bl{animation:bl 1.4s steps(1) infinite}@keyframes bl{0%,70%{opacity:1}71%,100%{opacity:.2}}</style>",
         f'<rect width="{W}" height="{H}" fill="#ffa94d"/>',
         f'<rect x="4" y="4" width="{W - 8}" height="{H - 8}" fill="#0d1117"/>',
         f'<rect x="440" y="24" width="4" height="{H - 48}" fill="#30363d"/>']

    def val(v):
        return "-" if stats is None else f"{v:,}".replace(",", ".")

    contrib = 0 if stats is None else stats["contrib"]
    level = max(1, int(math.sqrt(contrib)))
    s += text_rects("PLAYER", 28, 28, 3, "#ffa94d")
    lv = f"LV {level if stats else '-'}"
    s.append('<g class="bl">')
    s += text_rects(lv, 412 - text_width(lv, 3), 28, 3, "#7CFC00")
    s.append("</g>")

    rows = [
        ("fire", "#ff6b3d", "CONTRIBUTIONS", val(stats and stats["contrib"]), "LAST 365 DAYS"),
        ("pick", "#cfd8e3", "COMMITS", val(stats and stats["commits"]), "LAST 365 DAYS"),
        ("chest", "#c98a3a", "PUBLIC REPOS", val(stats and stats["repos"]), ""),
        ("star", "#ffe066", "STARS EARNED", val(stats and stats["stars"]), ""),
        ("user", "#7fd8ff", "FOLLOWERS", val(stats and stats["followers"]), ""),
    ]
    for i, (ic, col, label, v, note) in enumerate(rows):
        y = 70 + i * 42
        s += icon(ICONS[ic], col, 28, y)
        s += text_rects(label, 64, y + 3, 2, "#c9d1d9")
        s += text_rects(v, 412 - text_width(v, 3), y, 3, "#ffffff")

    # right: language "skill XP"
    s += text_rects("SKILL XP", 468, 28, 3, "#ffa94d")
    langs = [] if stats is None else stats["langs"]
    if not langs:
        s += text_rects("LOADING DATA...", 468, 80, 2, "#8b949e")
    for i, (name, color, pct) in enumerate(langs):
        y = 72 + i * 36
        aliases = {"Jupyter Notebook": "Jupyter", "Visual Basic .NET": "VB.NET"}
        label = aliases.get(name, name).upper()[:16]
        s += text_rects(label, 468, y, 2, "#c9d1d9")
        p = f"{pct:.1f}%"
        s += text_rects(p, 852 - text_width(p, 2), y, 2, "#8b949e")
        segs = 24
        filled = max(1, round(pct / 100 * segs))
        bx, by = 468, y + 18
        s.append(f'<rect x="{bx}" y="{by}" width="{segs * 16}" height="10" fill="#21262d"/>')
        s.append(f'<g class="grow" style="transform-origin:{bx}px {by}px;animation-delay:{i * 0.15:.2f}s">')
        for k in range(filled):
            s.append(f'<rect x="{bx + k * 16}" y="{by}" width="14" height="10" fill="{color}"/>')
        s.append("</g>")
    s.append("</svg>")
    with open(OUT, "w") as f:
        f.write("\n".join(s))


if __name__ == "__main__":
    data = None
    try:
        data = fetch()
    except Exception as e:  # keep the old/placeholder image on network errors
        print("fetch failed:", e, file=sys.stderr)
        if os.path.exists(OUT):
            sys.exit(0)
    build(data)
    print("stats built", "(live)" if data else "(placeholder)")
