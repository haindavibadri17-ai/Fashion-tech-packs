"""Flat technical sketches.

One geometry source drives both outputs:
  - render_svg()   -> inline SVG for the web UI
  - draw_pdf()     -> reportlab canvas drawing for the PDF report

Coordinates: 100x100 viewbox, y grows DOWN (flattened, front view).
Each path is a flat list of (x, y) points; the optional string "dashed"
as the last element marks a dashed line.
"""
import math

ACCENT = (0.706, 0.337, 0.176)  # #b4552d
INK = (0.11, 0.11, 0.11)


def _q(p0, p1, p2, n=8):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
        pts.append((x, y))
    return pts


def _neck(a, b, depth=20.5):
    return _q(a, ((a[0] + b[0]) / 2, depth), b, 7)


def _long_sleeve_body():
    """Body outline for long-sleeve garments (crew neck)."""
    return [
        (44, 13), (29, 11), (16, 16), (8, 64), (7, 78), (20, 79), (26, 40), (27, 33),
        (26, 88), (74, 88), (73, 33), (74, 40), (80, 79), (93, 78), (92, 64), (84, 16),
        (71, 11), (56, 13),
    ] + _neck((56, 13), (44, 13))


CUFF_L = [(8.2, 74.0), (19.2, 75.0), "dashed"]
CUFF_R = [(91.8, 74.0), (80.8, 75.0), "dashed"]
HEM_DASH = [(27.5, 85.2), (72.5, 85.2), "dashed"]


def _mats_shoulder_chest():
    return [
        {"a": (29, 6.5), "b": (71, 6.5), "label": "Shoulder", "lp": (50, 4.2)},
        {"a": (26, 42), "b": (74, 42), "label": "Chest", "lp": (50, 44.6)},
    ]


def _mat_length():
    return {"a": (96, 11), "b": (96, 88), "label": "Length", "vertical": True, "lp": (99, 49.5)}


MAT_SLEEVE_LS = {"a": (24.3, 9.5), "b": (2.3, 76.5), "label": "Sleeve", "lp": (9.3, 41.5)}


FLATS = {
    "tshirt": {
        "title": "T-Shirt — Front",
        "paths": [
            [
                (44, 13), (29, 11), (15, 17), (9, 33), (24, 29), (27, 33), (26, 88),
                (74, 88), (73, 33), (76, 29), (91, 33), (85, 17), (71, 11), (56, 13),
            ] + _neck((56, 13), (44, 13), 20.5),
            _q((55, 13.8), (50, 19.2), (45, 13.8), 7),
            [(10.6, 31.4), (23.4, 28.0)],
            [(89.4, 31.4), (76.6, 28.0)],
            HEM_DASH,
        ],
        "dots": [],
        "mats": [
            {"a": (29, 6.5), "b": (71, 6.5), "label": "Shoulder", "lp": (50, 4.2)},
            {"a": (26, 42), "b": (74, 42), "label": "Chest", "lp": (50, 44.6)},
            _mat_length(),
            {"a": (25.7, 8), "b": (5.7, 30), "label": "Sleeve", "lp": (12.2, 15.8)},
        ],
    },
    "top": {
        "title": "Top (long sleeve) — Front",
        "paths": [
            _long_sleeve_body(),
            _q((55, 13.8), (50, 19.2), (45, 13.8), 7),
            CUFF_L,
            CUFF_R,
            HEM_DASH,
        ],
        "dots": [],
        "mats": [
            {"a": (29, 6.5), "b": (71, 6.5), "label": "Shoulder", "lp": (50, 4.2)},
            {"a": (26, 42), "b": (74, 42), "label": "Chest", "lp": (50, 44.6)},
            _mat_length(),
            MAT_SLEEVE_LS,
        ],
    },
    "shirt": {
        "title": "Shirt (button-down) — Front",
        "paths": [
            _long_sleeve_body(),
            _q((55, 13.8), (50, 19.2), (45, 13.8), 7),
            [(44, 13), (36.5, 17), (41.5, 24.5), (48, 17.8)],
            [(56, 13), (63.5, 17), (58.5, 24.5), (52, 17.8)],
            [(47, 18), (47, 88)],
            [(53, 18), (53, 88)],
            CUFF_L,
            CUFF_R,
        ],
        "dots": [(50, 26, 0.9), (50, 39, 0.9), (50, 52, 0.9), (50, 65, 0.9), (50, 78, 0.9)],
        "mats": [
            {"a": (29, 6.5), "b": (71, 6.5), "label": "Shoulder", "lp": (50, 4.2)},
            {"a": (26, 42), "b": (74, 42), "label": "Chest", "lp": (50, 44.6)},
            _mat_length(),
            MAT_SLEEVE_LS,
        ],
    },
    "hoodie": {
        "title": "Hoodie — Front",
        "paths": [
            _long_sleeve_body(),
            [(42, 13), (39, 7), (44, 2.5), (56, 2.5), (61, 7), (58, 13)]
            + _q((58, 13), (50, 19), (42, 13), 7),
            [(36, 58), (30, 80), (70, 80), (64, 58)],
            [(47, 15.5), (46.2, 26)],
            [(53, 15.5), (53.8, 26)],
            CUFF_L,
            CUFF_R,
            HEM_DASH,
        ],
        "dots": [(46.2, 27, 0.7), (53.8, 27, 0.7)],
        "mats": [
            {"a": (29, 6.5), "b": (71, 6.5), "label": "Shoulder", "lp": (50, 4.2)},
            {"a": (26, 42), "b": (74, 42), "label": "Chest", "lp": (50, 44.6)},
            _mat_length(),
            MAT_SLEEVE_LS,
        ],
    },
    "jacket": {
        "title": "Jacket — Front",
        "paths": [
            _long_sleeve_body(),
            [(44, 12), (37, 15), (40, 21.5), (46.5, 16.5)],
            [(56, 12), (63, 15), (60, 21.5), (53.5, 16.5)],
            [(49, 17.5), (49, 88)],
            [(51.2, 17.5), (51.2, 88)],
            [(50.1, 18), (50.1, 87.5), "dashed"],
            [(29, 57), (39, 61)],
            [(71, 57), (61, 61)],
            CUFF_L,
            CUFF_R,
        ],
        "dots": [],
        "mats": [
            {"a": (29, 6.5), "b": (71, 6.5), "label": "Shoulder", "lp": (50, 4.2)},
            {"a": (26, 38), "b": (74, 38), "label": "Chest", "lp": (50, 40.6)},
            {"a": (26, 55), "b": (74, 55), "label": "Waist", "lp": (50, 57.6)},
            _mat_length(),
            MAT_SLEEVE_LS,
        ],
    },
    "pants": {
        "title": "Jeans / Trousers — Front",
        "paths": [
            [(31, 7), (69, 7), (69, 13), (31, 13)],
            [(31, 13), (26, 28), (23, 60), (22, 88), (38, 88), (39, 42), (50, 37),
             (61, 42), (62, 88), (78, 88), (77, 60), (74, 28), (69, 13)],
            [(50, 13), (50, 33)],
            _q((31, 14), (32, 24), (40, 16), 6),
            _q((69, 14), (68, 24), (60, 16), 6),
            [(35, 7), (35, 13)],
            [(45, 7), (45, 13)],
            [(55, 7), (55, 13)],
            [(65, 7), (65, 13)],
            [(23, 85.2), (37.5, 85.2), "dashed"],
            [(62.5, 85.2), (77, 85.2), "dashed"],
        ],
        "dots": [(31.5, 14.5, 0.7), (68.5, 14.5, 0.7), (50, 34.5, 0.7), (50, 10.2, 1.0)],
        "mats": [
            {"a": (31, 4), "b": (69, 4), "label": "Waist", "lp": (50, 1.8)},
            {"a": (24, 28), "b": (76, 28), "label": "Hip", "lp": (50, 30.6)},
            {"a": (50, 37), "b": (40, 86), "label": "Inseam", "lp": (46.8, 62)},
            {"a": (27, 9.5), "b": (15, 88.5), "label": "Outseam", "lp": (9.8, 49)},
            {"a": (54, 13.5), "b": (54, 37), "label": "Rise", "lp": (58.6, 25.5)},
        ],
    },
    "shorts": {
        "title": "Shorts — Front",
        "paths": [
            [(31, 7), (69, 7), (69, 13), (31, 13)],
            [(31, 13), (26, 28), (23, 48), (22, 56), (38, 56), (39, 42), (50, 37),
             (61, 42), (62, 56), (78, 56), (77, 48), (74, 28), (69, 13)],
            [(50, 13), (50, 33)],
            _q((31, 14), (32, 24), (40, 16), 6),
            _q((69, 14), (68, 24), (60, 16), 6),
            [(35, 7), (35, 13)],
            [(45, 7), (45, 13)],
            [(55, 7), (55, 13)],
            [(65, 7), (65, 13)],
            [(23, 53.2), (37.5, 53.2), "dashed"],
            [(62.5, 53.2), (77, 53.2), "dashed"],
        ],
        "dots": [(31.5, 14.5, 0.7), (68.5, 14.5, 0.7), (50, 34.5, 0.7), (50, 10.2, 1.0)],
        "mats": [
            {"a": (31, 4), "b": (69, 4), "label": "Waist", "lp": (50, 1.8)},
            {"a": (24, 27), "b": (76, 27), "label": "Hip", "lp": (50, 29.6)},
            {"a": (50, 37), "b": (40, 54), "label": "Inseam", "lp": (46.8, 45.5)},
            {"a": (27, 9.5), "b": (15, 54), "label": "Outseam", "lp": (10, 32)},
        ],
    },
    "dress": {
        "title": "Dress (A-line) — Front",
        "paths": [
            [
                (45, 12), (30, 10.5), (19, 15), (14, 27), (24, 25), (27, 31), (23, 50),
                (16, 88), (84, 88), (77, 50), (73, 31), (76, 25), (86, 27), (81, 15),
                (70, 10.5), (55, 12), (50, 18.5),
            ],
            [(25.8, 42), (74.2, 42), "dashed"],
        ],
        "dots": [],
        "mats": [
            {"a": (30, 6.5), "b": (70, 6.5), "label": "Shoulder", "lp": (50, 4.2)},
            {"a": (27, 34), "b": (73, 34), "label": "Chest", "lp": (50, 36.6)},
            {"a": (25.5, 42), "b": (74.5, 42), "label": "Waist", "lp": (50, 44.6)},
            {"a": (22, 60), "b": (78, 60), "label": "Hip", "lp": (50, 62.6)},
            {"a": (96, 10.5), "b": (96, 88), "label": "Length", "vertical": True, "lp": (99, 49.5)},
            {"a": (27.1, 7.7), "b": (11.1, 24.2), "label": "Sleeve", "lp": (15.8, 12.4)},
        ],
    },
    "skirt": {
        "title": "Skirt (A-line) — Front",
        "paths": [
            [(36, 8), (64, 8), (64, 14), (36, 14)],
            [(36, 14), (26, 88), (74, 88), (64, 14)],
            [(44, 16), (40, 86), "dashed"],
            [(56, 16), (60, 86), "dashed"],
            [(27, 85), (73, 85), "dashed"],
        ],
        "dots": [],
        "mats": [
            {"a": (34, 4.5), "b": (66, 4.5), "label": "Waist", "lp": (50, 2.2)},
            {"a": (28, 34), "b": (72, 34), "label": "Hip", "lp": (50, 36.6)},
            {"a": (90, 14), "b": (90, 88), "label": "Length", "vertical": True, "lp": (93.4, 51)},
            {"a": (26, 92), "b": (74, 92), "label": "Hem width", "lp": (50, 95.6)},
        ],
    },
}


def _tick(a, b, length=2.2):
    """Perpendicular end-tick segment for a measurement line."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy) or 1
    px, py = -dy / d, dx / d
    k = length / 2
    return [(a[0] + px * k, a[1] + py * k), (a[0] - px * k, a[1] - py * k)]


def render_svg(flat_key, width=520):
    flat = FLATS[flat_key]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
        f'width="{width}" role="img" aria-label="{flat["title"]}">'
    ]
    for p in flat["paths"]:
        dashed = isinstance(p[-1], str)
        pts = p[:-1] if dashed else p
        d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)
        attrs = ' stroke-dasharray="2.4 2"' if dashed else ""
        parts.append(f'<path d="{d}" fill="none" stroke="#1c1c1c" '
                     f'stroke-width="1" stroke-linejoin="round" stroke-linecap="round"{attrs}/>')
    for (cx, cy, r) in flat.get("dots", []):
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#1c1c1c"/>')
    for m in flat["mats"]:
        a, b = m["a"], m["b"]
        for (t1, t2) in (_tick(a, b), _tick(b, a)):
            parts.append(f'<line x1="{t1[0]:.2f}" y1="{t1[1]:.2f}" x2="{t2[0]:.2f}" y2="{t2[1]:.2f}" '
                         f'stroke="#b4552d" stroke-width="0.55"/>')
        parts.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" '
                     f'stroke="#b4552d" stroke-width="0.55"/>')
        lx, ly = m["lp"]
        parts.append(f'<text x="{lx}" y="{ly}" font-size="3.4" fill="#b4552d" '
                     f'font-family="Helvetica, Arial, sans-serif" text-anchor="middle">{m["label"]}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def draw_pdf(canvas, flat_key, x, y, w):
    """Draw the flat on a reportlab canvas. (x, y) = bottom-left corner, w = width."""
    from reportlab.lib import colors as _c
    ink = _c.Color(*INK)
    accent = _c.Color(*ACCENT)
    flat = FLATS[flat_key]
    s = w / 100.0

    def X(px):
        return x + px * s

    def Y(py):
        return y + w - py * s

    canvas.saveState()
    canvas.setStrokeColor(ink)
    canvas.setFillColor(ink)
    for p in flat["paths"]:
        dashed = isinstance(p[-1], str)
        pts = p[:-1] if dashed else p
        if dashed:
            canvas.setDash(2.4 * s, 2.0 * s)
        canvas.setLineWidth(1.0 * s)
        path = canvas.beginPath()
        path.moveTo(X(pts[0][0]), Y(pts[0][1]))
        for (px, py) in pts[1:]:
            path.lineTo(X(px), Y(py))
        canvas.drawPath(path, stroke=1, fill=0)
        canvas.setDash()
    for (cx, cy, r) in flat.get("dots", []):
        canvas.circle(X(cx), Y(cy), r * s, stroke=0, fill=1)
    # measurement lines
    canvas.setStrokeColor(accent)
    canvas.setFillColor(accent)
    for m in flat["mats"]:
        a, b = m["a"], m["b"]
        canvas.setLineWidth(0.55 * s)
        path = canvas.beginPath()
        path.moveTo(X(a[0]), Y(a[1]))
        path.lineTo(X(b[0]), Y(b[1]))
        canvas.drawPath(path, stroke=1, fill=0)
        for (t1, t2) in (_tick(a, b), _tick(b, a)):
            path = canvas.beginPath()
            path.moveTo(X(t1[0]), Y(t1[1]))
            path.lineTo(X(t2[0]), Y(t2[1]))
            canvas.drawPath(path, stroke=1, fill=0)
        lx, ly = m["lp"]
        canvas.setFont("Helvetica", 3.4 * s)
        if m.get("vertical"):
            canvas.saveState()
            canvas.translate(X(lx), Y(ly))
            canvas.rotate(90)
            canvas.drawCentredString(0, 0, m["label"])
            canvas.restoreState()
        else:
            canvas.drawCentredString(X(lx), Y(ly), m["label"])
    canvas.restoreState()
