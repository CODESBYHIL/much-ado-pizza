# Writes ring.html: the hero's ring of pies, placed on an ellipse inside a fixed-shape stage.
# Desktop: 14 frames, evenly spaced by arc length. Phone: 10 frames on the top and bottom arcs only,
# so the sides stay clear for the headline.
import html, math, os

ROOT = os.path.dirname(os.path.abspath(__file__))
ITEMS = [  # image, label: only pies on the live menu, each with the photo the shop itself named after it
    ("taming", "Taming of the Chew · $25"), ("titania", "Titania’s Bounty · $32"),
    ("henry8", "Henry the 8 · $35"), ("groundling", "Groundling · $24"),
    ("act5", "Act Five · $33"), ("orig", "Much Ado Original Cheese · $22"),
    ("tempest", "Tempest · $28"), ("portia", "Portia’s Pesto Pizza · $32"),
    ("quatrain", "Quatrain · $28"), ("viola", "Viola’s Veggie · $30"),
    ("polish2022", "Ham Let · $32"),
]
TARGET = {  # ring photo -> the menu row it opens
    "taming": "pie-taming-of-the-chew", "titania": "pie-titanias-bounty", "henry8": "pie-henry-the-8",
    "groundling": "pie-groundling", "act5": "pie-act-five", "orig": "pie-much-ado-original-cheese",
    "tempest": "pie-tempest", "portia": "pie-portias-pesto-pizza", "quatrain": "pie-quatrain",
    "viola": "pie-violas-veggie", "polish2022": "pie-ham-let",
}
PHONE = [0, 1, 2, 3, 5, 6, 7, 10]  # which items the phone shows: 4 on top, 4 below


def even(n, rx, ry, skip=None):
    """n angles spaced by equal arc length on an ellipse, starting at the top; skip=(deg) clears the sides."""
    ts = [-math.pi / 2 + 2 * math.pi * j / 4000 for j in range(4001)]
    if skip:
        ts = [t for t in ts if abs(math.degrees(math.asin(max(-1, min(1, math.sin(t)))))) >= skip]
    L = [0.0]
    for a, b in zip(ts, ts[1:]):
        jump = abs(b - a) > 0.01
        L.append(L[-1] + (0 if jump else math.hypot(rx * (math.cos(b) - math.cos(a)), ry * (math.sin(b) - math.sin(a)))))
    out = []
    for i in range(n):
        target = (i + 0.5 * (skip is not None)) / n * L[-1]
        out.append(next(t for t, l in zip(ts, L) if l >= target))
    return out


# stage units are % of the stage box; desktop stage is 1.75:1, phone stage is 0.56:1
dk = even(len(ITEMS), 43, 40 * 1 / 1.75)
ph = even(len(PHONE), 40, 43 / 0.56, skip=30)
rows = []
for i, (img, label) in enumerate(ITEMS):
    t = dk[i]
    x, y = 50 + 43 * math.cos(t), 50 + 40 * math.sin(t)
    rot = (-5, 4, -3, 5, -4, 3)[i % 6]
    style = f"--x:{x:.2f}%;--y:{y:.2f}%;--r:{rot}deg"
    cls = "frame"
    if i in PHONE:
        tm = ph[PHONE.index(i)]
        style += f";--mx:{50 + 40 * math.cos(tm):.2f}%;--my:{50 + 43 * math.sin(tm):.2f}%"
    else:
        cls += " not-m"
    name = label.split(" · ")[0]
    eager = ' fetchpriority="high"' if i < 5 else ""
    rows.append(f'<a class="{cls}" href="#{TARGET.get(img, "menu")}" data-label="{html.escape(label)}" style="{style}">'
                f'<img{eager} src="web/{img}-s.jpg" alt="{html.escape(name)}" width="420" height="525"></a>')
open(os.path.join(ROOT, "ring.html"), "w", encoding="utf-8").write("\n      ".join(rows))
print(len(rows), "frames")
