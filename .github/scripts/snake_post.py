"""Tidy the snk output: drop the progress bar, keep the snake inside the grid, fade it out once it has eaten everything."""
import re
import sys

for path in sys.argv[1:]:
    svg = open(path).read()

    # progress bar under the grid
    svg = re.sub(r'<rect class="u u\d+"[^>]*/>', "", svg)

    # crop the picture to the grid, so the snake's start and exit rows above it are never drawn
    cells = [(float(x), float(y)) for x, y in re.findall(r'<rect class="c[^"]*" x="([\d.]+)" y="([\d.]+)"', svg)]
    max_x = max(x for x, _ in cells) - 2
    max_y = max(y for _, y in cells) - 2
    w, h = max_x + 16, max_y + 16
    svg = re.sub(r'viewBox="[^"]*" width="\d+" height="\d+"', f'viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}"', svg, count=1)

    css = svg[svg.index("<style>"):svg.index("</style>")]

    # snk sometimes routes the snake along the outside edge; keep it on the last row instead
    def clamp(block):
        def move(m):
            x, y = float(m.group(1)), float(m.group(2))
            return f"translate({min(max(x, 0), max_x):g}px,{min(y, max_y):g}px)"
        return re.sub(r"translate\((-?[\d.]+)px,(-?[\d.]+)px\)", move, block.group(0))

    new_css = re.sub(r"@keyframes s\d\{.*?\}\}", clamp, css)

    # the percentage of the loop at which the last cell is eaten, then fade the snake out
    last = max(float(m.group(1)) for m in re.finditer(r"@keyframes c\d+\{([\d.]+)%\{", css))
    new_css += (f"@keyframes fade{{0%,{last + 1:.2f}%{{opacity:1}}"
                f"{last + 5:.2f}%,99.8%{{opacity:0}}100%{{opacity:1}}}}")
    new_css = re.sub(r"(\.s\.s\d\{[^}]*animation-name:)(s\d)\}", r"\1\2,fade}", new_css)

    svg = svg.replace(css, new_css)
    open(path, "w").write(svg)
