"""Draw a card of the languages used across a user's public, non-fork repos."""
import json
import os
import sys
import urllib.request
from html import escape

USER = sys.argv[1]
OUT = sys.argv[2]
TOP = 8

COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Dart": "#00B4AB",
    "Kotlin": "#A97BFF", "Java": "#b07219", "HTML": "#e34c26", "CSS": "#663399", "Shell": "#89e051",
    "Jupyter Notebook": "#DA5B0B", "C++": "#f34b7d", "C": "#555555", "Swift": "#F05138",
    "PHP": "#4F5D95", "Go": "#00ADD8", "Rust": "#dea584", "Dockerfile": "#384d54",
    "SCSS": "#c6538c", "PowerShell": "#012456", "Batchfile": "#C1F12E",
}


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


totals = {}
page = 1
while True:
    repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner")
    if not repos:
        break
    for repo in repos:
        if repo["fork"]:
            continue
        for lang, size in get(repo["languages_url"]).items():
            totals[lang] = totals.get(lang, 0) + size
    page += 1

ranked = sorted(totals.items(), key=lambda kv: -kv[1])
shown = ranked[:TOP]
rest = sum(size for _, size in ranked[TOP:])
if rest:
    shown.append(("Other", rest))
total = sum(size for _, size in shown)

W, H, PAD = 420, 256, 24
BAR_W = W - 2 * PAD
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">',
    f'<rect width="{W}" height="{H}" rx="10" fill="#282c34"/>',
    f'<text x="{PAD}" y="38" font-size="17" font-weight="600" fill="#e4bf7a">Languages I use</text>',
    f'<clipPath id="bar"><rect x="{PAD}" y="54" width="{BAR_W}" height="10" rx="5"/></clipPath>',
    '<g clip-path="url(#bar)">',
]
x = PAD
for lang, size in shown:
    w = BAR_W * size / total
    parts.append(f'<rect x="{x:.2f}" y="54" width="{w + 0.5:.2f}" height="10" fill="{COLORS.get(lang, "#8b949e")}"/>')
    x += w
parts.append("</g>")

col_w = BAR_W // 2
for i, (lang, size) in enumerate(shown):
    cx = PAD + (i % 2) * col_w
    cy = 94 + (i // 2) * 30
    color = COLORS.get(lang, "#8b949e")
    parts.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{color}"/>')
    parts.append(f'<text x="{cx + 18}" y="{cy}" font-size="13" fill="#abb2bf">{escape(lang)}</text>')
    parts.append(
        f'<text x="{cx + col_w - 18}" y="{cy}" font-size="13" fill="#e4bf7a" text-anchor="end">'
        f'{100 * size / total:.1f}%</text>'
    )
parts.append("</svg>")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    f.write("\n".join(parts))
print(", ".join(f"{l} {100 * s / total:.1f}%" for l, s in shown))
