"""Tidy the snk output: drop the progress bar, fade the snake out once it has eaten everything."""
import re
import sys

for path in sys.argv[1:]:
    svg = open(path).read()

    # progress bar under the grid, and the space it took
    svg = re.sub(r'<rect class="u u\d+"[^>]*/>', "", svg)
    svg = svg.replace('viewBox="-16 -32 880 192" width="880" height="192"',
                      'viewBox="-16 -12 880 136" width="880" height="136"')

    # the percentage of the loop at which the last cell is eaten
    css = svg[svg.index("<style>"):svg.index("</style>")]
    last = max(float(m.group(1)) for m in re.finditer(r"@keyframes c\d+\{([\d.]+)%\{", css))
    fade = (f"@keyframes fade{{0%,{last + 1:.2f}%{{opacity:1}}"
            f"{last + 5:.2f}%,99.8%{{opacity:0}}100%{{opacity:1}}}}")

    svg = svg.replace("</style>", fade + "</style>", 1)
    svg = re.sub(r"(\.s\.s\d\{[^}]*animation-name:)(s\d)\}", r"\1\2,fade}", svg)
    open(path, "w").write(svg)
