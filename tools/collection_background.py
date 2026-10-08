"""Draws the Cold Steel Mix collection background: the patch icon and the
playset's name on the left, Tron-style lines on the right, and a fade between
them along a forward diagonal through the middle.

    python3 tools/collection_background.py out.svg
    rsvg-convert -w 1920 -h 1080 out.svg -o out.png

The letters are drawn as lines, not set in a font, so it renders the same
anywhere, the dev container included, which has no fonts.
"""

import random
import re
import sys
from itertools import pairwise
from pathlib import Path

W, H = 1920, 1080
ICON = Path(__file__).parent.parent / "src/stellaris_patcher/data/patch-icon.svg"

EMERALD = "#5fe0a0"
EMERALD_DEEP = "#1fa866"
MINT = "#b4f2d2"
FROST = "#7fb8e6"
CYAN = "#7fd8ff"

# The fade: across a "/" line through the middle, `FADE` px each side of it.
FADE = 150

# The grid floor: horizon, vanishing point, and how far apart its lines are at
# the bottom edge (depth 1).
HORIZON = 640
VANISH = 1450
SPACING = 150

# Letters on a 6 x 8 grid, as SVG path data: squared, with cut corners.
LETTERS = {
    "C": "M6 0H1.5L0 1.5V6.5L1.5 8H6",
    "O": "M1.5 0H4.5L6 1.5V6.5L4.5 8H1.5L0 6.5V1.5Z",
    "L": "M0 0V8H6",
    "D": "M0 0H4.2L6 1.8V6.2L4.2 8H0Z",
    "S": "M6 0H1.5L0 1.5V2.5L1.5 4H4.5L6 5.5V6.5L4.5 8H0",
    "T": "M0 0H6M3 0V8",
    "E": "M6 0H0V8H6M0 4H4.5",
    "M": "M0 8V0L3 3.5L6 0V8",
    "I": "M1.5 0H4.5M3 0V8M1.5 8H4.5",
    "X": "M0 0L6 8M6 0L0 8",
}


def word(text: str, x: float, y: float, size: float, gap: float = 2.6) -> str:
    """One word's paths, with its top left corner at (x, y). `size` is the
    cap height in px."""
    unit = size / 8
    paths = []
    for i, letter in enumerate(text):
        at = x + i * (6 + gap) * unit
        paths.append(
            f'<path d="{LETTERS[letter]}" transform="translate({at:.1f} {y:.1f}) scale({unit:.3f})"'
            ' vector-effect="non-scaling-stroke"/>'
        )
    return "".join(paths)


def icon(x: float, y: float, size: float) -> str:
    """The patch icon, placed and sized, with its ids prefixed so they can't
    clash with ours."""
    svg = ICON.read_text("utf-8")
    inner = svg[svg.index(">", svg.index("<svg")) + 1 : svg.rindex("</svg>")]
    inner = re.sub(r'id="([^"]+)"', r'id="icon-\1"', inner)
    inner = re.sub(r"url\(#([^)]+)\)", r"url(#icon-\1)", inner)
    return f'<g transform="translate({x} {y}) scale({size / 256:.4f})">{inner}</g>'


def floor(u: float, z: float) -> tuple[float, float]:
    """A point on the grid floor: `u` grid lines right of the vanishing point,
    at depth `z` (1 is the bottom edge)."""
    return VANISH + u * SPACING / z, HORIZON + (H - HORIZON) / z


def grid() -> str:
    lines = []
    for u in range(-18, 14):
        bx, by = floor(u, 1)
        # Extend each line past the bottom edge, so none ends in view.
        ex, ey = VANISH + (bx - VANISH) * 1.2, HORIZON + (by - HORIZON) * 1.2
        lines.append(f'<line x1="{VANISH}" y1="{HORIZON}" x2="{ex:.1f}" y2="{ey:.1f}"/>')
    z = 0.8
    while z < 60:
        _, y = floor(0, z)
        lines.append(f'<line x1="0" y1="{y:.1f}" x2="{W}" y2="{y:.1f}"/>')
        z *= 1.28
    return "".join(lines)


def trail(steps: list[tuple[float, float]], colour: str, wall: float = 70) -> str:
    """A light cycle's trail along the grid: its wall of light, its glowing
    line and the cycle at its head."""
    points = [floor(u, z) for u, z in steps]
    walls = []
    for (u1, z1), (u2, z2) in pairwise(steps):
        (x1, y1), (x2, y2) = floor(u1, z1), floor(u2, z2)
        walls.append(
            f'<polygon points="{x1:.1f},{y1:.1f} {x2:.1f},{y2:.1f} '
            f'{x2:.1f},{y2 - wall / z2:.1f} {x1:.1f},{y1 - wall / z1:.1f}"/>'
        )
        walls.append(
            f'<line x1="{x1:.1f}" y1="{y1 - wall / z1:.1f}" x2="{x2:.1f}" y2="{y2 - wall / z2:.1f}"'
            f' stroke="{colour}" stroke-width="1.5" opacity="0.8"/>'
        )
    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    hx, hy = points[-1]
    head_z = steps[-1][1]
    size = 40 / head_z
    return (
        f'<g fill="{colour}" fill-opacity="0.28">{"".join(walls)}</g>'
        f'<polyline points="{path}" fill="none" stroke="{colour}" stroke-width="10"'
        ' stroke-linejoin="miter" opacity="0.55" filter="url(#blur)"/>'
        f'<polyline points="{path}" fill="none" stroke="#f2fff8" stroke-width="2.5"'
        ' stroke-linejoin="miter"/>'
        f'<g transform="translate({hx:.1f} {hy:.1f})" filter="url(#glow)">'
        f'<polygon points="0,{-size * 1.1:.1f} {size * 0.6:.1f},0 0,{size * 0.25:.1f} {-size * 0.6:.1f},0"'
        f' fill="#f2fff8" stroke="{colour}" stroke-width="2"/></g>'
    )


def disc(cx: float, cy: float, r: float) -> str:
    """A Tron identity disc, seen face on."""
    ticks = []
    for i in range(48):
        long = i % 4 == 0
        ticks.append(
            f'<line x1="0" y1="{-r * 0.78:.1f}" x2="0" y2="{-r * (0.71 if long else 0.75):.1f}"'
            f' transform="rotate({i * 7.5})"/>'
        )
    return f"""
    <g transform="translate({cx} {cy})" fill="none">
      <circle r="{r * 1.08:.1f}" stroke="{EMERALD}" stroke-width="14" opacity="0.35" filter="url(#blur)"/>
      <circle r="{r:.1f}" stroke="{MINT}" stroke-width="4" filter="url(#glow)"/>
      <circle r="{r * 0.93:.1f}" stroke="{EMERALD}" stroke-width="9" stroke-dasharray="{r * 0.3:.1f} {r * 0.08:.1f}" opacity="0.85"/>
      <path d="M{-r * 1.22:.1f} 0A{r * 1.22:.1f} {r * 1.22:.1f} 0 0 1 {-r * 0.43:.1f} {-r * 1.14:.1f}" stroke="{FROST}" stroke-width="3" opacity="0.7"/>
      <path d="M{r * 1.22:.1f} 0A{r * 1.22:.1f} {r * 1.22:.1f} 0 0 1 {r * 0.43:.1f} {r * 1.14:.1f}" stroke="{FROST}" stroke-width="3" opacity="0.7"/>
      <g stroke="{FROST}" stroke-width="2" opacity="0.8">{"".join(ticks)}</g>
      <circle r="{r * 0.55:.1f}" stroke="{FROST}" stroke-width="3" opacity="0.9" filter="url(#glow)"/>
      <circle r="{r * 0.55:.1f}" fill="#081019" opacity="0.6"/>
      <circle r="{r * 0.22:.1f}" fill="#0b1a14" stroke="{EMERALD}" stroke-width="4" filter="url(#glow)"/>
      <circle r="{r * 0.07:.1f}" fill="{MINT}"/>
    </g>"""


def skyline(rng: random.Random) -> str:
    towers = []
    x = 980.0
    while x < W:
        w = rng.uniform(26, 70)
        h = rng.choice((rng.uniform(16, 50), rng.uniform(40, 110)))
        towers.append(f'<rect x="{x:.1f}" y="{HORIZON - h:.1f}" width="{w:.1f}" height="{h:.1f}"/>')
        if h > 60 and rng.random() < 0.5:
            towers.append(
                f'<line x1="{x + 6:.1f}" y1="{HORIZON - h + 10:.1f}" x2="{x + w - 6:.1f}"'
                f' y2="{HORIZON - h + 10:.1f}"/>'
            )
        x += w + rng.uniform(4, 30)
    return "".join(towers)


def circuits() -> str:
    """Traces running in from the top right edge, each ending in a node."""
    traces = [
        ((W, 70), [(1790, 70), (1750, 110), (1650, 110)]),
        ((W, 120), [(1830, 120), (1790, 160), (1720, 160)]),
        ((1700, 0), [(1700, 40), (1660, 80), (1560, 80)]),
        ((W, 200), [(1880, 200), (1850, 230)]),
        ((1600, 0), [(1600, 26), (1570, 56), (1480, 56)]),
        ((W, 960), [(1860, 960), (1830, 930), (1830, 860)]),
    ]
    out = []
    for start, points in traces:
        path = " ".join(f"{x},{y}" for x, y in [start, *points])
        ex, ey = points[-1]
        out.append(f'<polyline points="{path}"/><circle cx="{ex}" cy="{ey}" r="5" fill="#081019"/>')
    return "".join(out)


def stars(rng: random.Random) -> str:
    out = []
    for _ in range(170):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r, o = rng.uniform(0.5, 1.8), rng.uniform(0.15, 0.75)
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" opacity="{o:.2f}"/>')
    return "".join(out)


def background() -> str:
    rng = random.Random(1010586431)
    mid_x, mid_y = W / 2, H / 2
    d = FADE / 2**0.5  # along both axes: the fade runs at right angles to the "/"
    logo_x, logo_y, logo = 120, 230, 320
    text_x, size, line = 480, 82, 108
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <!-- Made by tools/collection_background.py. Change that, not this. -->
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#1c2838"/>
      <stop offset="1" stop-color="#05080d"/>
    </linearGradient>
    <radialGradient id="frost" gradientUnits="userSpaceOnUse" cx="{logo_x + logo / 2 + 200}" cy="{logo_y + logo / 2}" r="760">
      <stop offset="0" stop-color="{FROST}" stop-opacity="0.22"/>
      <stop offset="1" stop-color="{FROST}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="vignette" cx="0.5" cy="0.5" r="0.75">
      <stop offset="0.6" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.55"/>
    </radialGradient>
    <linearGradient id="fade" gradientUnits="userSpaceOnUse" x1="{mid_x - d:.1f}" y1="{mid_y - d:.1f}" x2="{mid_x + d:.1f}" y2="{mid_y + d:.1f}">
      <stop offset="0" stop-color="#000"/>
      <stop offset="0.5" stop-color="#777"/>
      <stop offset="1" stop-color="#fff"/>
    </linearGradient>
    <mask id="right" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">
      <rect width="{W}" height="{H}" fill="url(#fade)"/>
    </mask>
    <linearGradient id="floor" gradientUnits="userSpaceOnUse" x1="0" y1="{HORIZON}" x2="0" y2="{H}">
      <stop offset="0" stop-color="#0b1d18"/>
      <stop offset="1" stop-color="#04070b"/>
    </linearGradient>
    <linearGradient id="gridline" gradientUnits="userSpaceOnUse" x1="0" y1="{HORIZON}" x2="0" y2="{H}">
      <stop offset="0" stop-color="{EMERALD}" stop-opacity="0.1"/>
      <stop offset="0.35" stop-color="{EMERALD}" stop-opacity="0.45"/>
      <stop offset="1" stop-color="{EMERALD}" stop-opacity="0.8"/>
    </linearGradient>
    <linearGradient id="horizon" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{EMERALD}" stop-opacity="0"/>
      <stop offset="0.5" stop-color="{EMERALD}" stop-opacity="0.45"/>
      <stop offset="1" stop-color="{EMERALD}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="steel" gradientUnits="userSpaceOnUse" x1="0" y1="{logo_y}" x2="0" y2="{logo_y + line + size}">
      <stop offset="0" stop-color="#eef4fa"/>
      <stop offset="1" stop-color="#8fa3b8"/>
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="blur" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="8"/>
    </filter>
    <filter id="soft" x="-10%" y="-10%" width="120%" height="120%">
      <feGaussianBlur stdDeviation="1.6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <g fill="#cfe2f5">{stars(rng)}</g>

  <!-- the right: Tron-style lines, faded in across the diagonal -->
  <g mask="url(#right)">
    <g fill="none" stroke="{FROST}" stroke-width="2" opacity="0.45">{circuits()}</g>
    {disc(1590, 330, 165)}
    <g fill="#070d13" stroke="{EMERALD}" stroke-width="1.5" stroke-opacity="0.45">{skyline(rng)}</g>
    <rect x="0" y="{HORIZON}" width="{W}" height="{H - HORIZON}" fill="url(#floor)"/>
    <g stroke="url(#gridline)" stroke-width="1.6" filter="url(#soft)">{grid()}</g>
    <rect x="0" y="{HORIZON - 60}" width="{W}" height="120" fill="url(#horizon)"/>
    <line x1="0" y1="{HORIZON}" x2="{W}" y2="{HORIZON}" stroke="{MINT}" stroke-width="2" filter="url(#glow)"/>
    {trail([(-3.0, 0.8), (-3.0, 2.2), (2.0, 2.2), (2.0, 5.5), (5.0, 5.5)], EMERALD)}
    {trail([(6.5, 0.8), (6.5, 1.5), (4.0, 1.5), (4.0, 3.2)], CYAN)}
  </g>

  <!-- the left: the icon and the playset's name -->
  <rect width="{W}" height="{H}" fill="url(#frost)"/>
  {icon(logo_x, logo_y, logo)}
  <g fill="none" stroke="url(#steel)" stroke-width="9" stroke-linecap="square" stroke-linejoin="miter">
    {word("COLD", text_x, logo_y + 18, size)}
    {word("STEEL", text_x, logo_y + 18 + line, size)}
  </g>
  <g fill="none" stroke="{EMERALD}" stroke-width="9" stroke-linecap="square" stroke-linejoin="miter" filter="url(#glow)">
    {word("MIX", text_x, logo_y + 18 + 2 * line, size)}
  </g>
  <line x1="{text_x + 3 * (6 + 2.6) * size / 8 + 10:.0f}" y1="{logo_y + 18 + 2 * line + size / 2:.0f}"
        x2="{text_x + 5 * (6 + 2.6) * size / 8 - 2.6 * size / 8:.0f}" y2="{logo_y + 18 + 2 * line + size / 2:.0f}"
        stroke="{EMERALD_DEEP}" stroke-width="3" opacity="0.8"/>

  <rect width="{W}" height="{H}" fill="url(#vignette)"/>
</svg>
"""


if __name__ == "__main__":
    Path(sys.argv[1]).write_text(background(), "utf-8")
