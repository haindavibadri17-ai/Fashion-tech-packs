"""Local image analysis tools — no external services required.

Extracts: dominant colour palette (k-means), garment foreground crop,
structure profile (row widths), brightness/contrast, and a thumbnail.
"""
import io
import os

import numpy as np
from PIL import Image, ImageOps

NAMED_COLORS = [
    ("Black", (20, 20, 20)), ("Charcoal", (55, 58, 62)), ("Dark Grey", (90, 93, 96)),
    ("Grey", (128, 130, 132)), ("Light Grey", (180, 180, 180)), ("Silver", (200, 202, 205)),
    ("White", (248, 248, 246)), ("Off-White", (240, 238, 230)), ("Ivory", (250, 248, 235)),
    ("Cream", (245, 235, 210)), ("Navy", (23, 32, 58)), ("Dark Blue", (35, 52, 88)),
    ("Royal Blue", (43, 80, 152)), ("Blue", (70, 120, 180)), ("Denim Blue", (96, 125, 158)),
    ("Washed Denim", (150, 172, 192)), ("Sky Blue", (140, 180, 215)), ("Light Blue", (185, 215, 235)),
    ("Red", (178, 34, 34)), ("Burgundy", (100, 22, 38)), ("Maroon", (90, 25, 40)),
    ("Wine", (80, 20, 45)), ("Orange", (220, 100, 30)), ("Rust", (160, 60, 30)),
    ("Mustard", (200, 155, 40)), ("Gold", (190, 155, 60)), ("Yellow", (235, 205, 70)),
    ("Green", (34, 88, 52)), ("Forest Green", (25, 60, 40)), ("Olive", (105, 105, 60)),
    ("Army Green", (70, 80, 50)), ("Khaki", (155, 140, 100)), ("Beige", (215, 195, 160)),
    ("Tan", (190, 160, 120)), ("Camel", (170, 130, 80)), ("Brown", (110, 75, 45)),
    ("Chocolate", (75, 50, 30)), ("Coffee", (55, 40, 28)), ("Pink", (235, 160, 170)),
    ("Rose", (210, 120, 140)), ("Magenta", (170, 50, 110)), ("Purple", (95, 60, 130)),
    ("Lavender", (185, 170, 210)), ("Teal", (20, 110, 110)), ("Turquoise", (60, 170, 170)),
    ("Brown-Tan", (140, 105, 70)),
]

# Suggested Pantone TCX references (approximate — always verify against a physical swatch).
PANTONE_SUGGESTED = {
    "Black": "19-0303 TCX", "Charcoal": "19-0405 TCX", "Dark Grey": "17-1503 TCX",
    "Grey": "16-1514 TCX", "Light Grey": "14-0317 TCX", "Silver": "14-0317 TCX",
    "White": "11-0601 TCX", "Off-White": "11-0602 TCX", "Ivory": "11-0602 TCX",
    "Cream": "12-0701 TCX", "Navy": "19-4026 TCX", "Dark Blue": "19-4020 TCX",
    "Royal Blue": "19-4052 TCX", "Blue": "19-4131 TCX", "Denim Blue": "19-4131 TCX",
    "Washed Denim": "15-4518 TCX", "Sky Blue": "15-4618 TCX", "Light Blue": "13-4313 TCX",
    "Red": "18-1664 TCX", "Burgundy": "19-1737 TCX", "Maroon": "19-1737 TCX",
    "Wine": "19-1722 TCX", "Orange": "16-1451 TCX", "Rust": "18-1435 TCX",
    "Mustard": "15-1054 TCX", "Gold": "14-1054 TCX", "Yellow": "13-0651 TCX",
    "Green": "18-6330 TCX", "Forest Green": "19-5317 TCX", "Olive": "18-0746 TCX",
    "Army Green": "18-0732 TCX", "Khaki": "15-1130 TCX", "Beige": "14-1112 TCX",
    "Tan": "15-1221 TCX", "Camel": "15-1221 TCX", "Brown": "18-1142 TCX",
    "Chocolate": "19-1118 TCX", "Coffee": "19-1219 TCX", "Pink": "14-1511 TCX",
    "Rose": "17-2034 TCX", "Magenta": "19-2540 TCX", "Purple": "19-3025 TCX",
    "Lavender": "14-3910 TCX", "Teal": "18-4529 TCX", "Turquoise": "15-5539 TCX",
    "Brown-Tan": "16-1336 TCX",
}


def name_color(rgb):
    r, g, b = rgb
    best, best_d = None, None
    for name, (nr, ng, nb) in NAMED_COLORS:
        d = (r - nr) ** 2 + (g - ng) ** 2 + (b - nb) ** 2
        if best_d is None or d < best_d:
            best, best_d = name, d
    return best


def _kmeans(pixels, k=5, iters=30, seed=7):
    """Tiny deterministic k-means over an (N,3) float array."""
    rng = np.random.default_rng(seed)
    n = pixels.shape[0]
    idx = rng.choice(n, size=k, replace=False)
    centers = pixels[idx].copy()
    labels = np.zeros(n, dtype=np.int32)
    for _ in range(iters):
        d = ((pixels[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
        new_labels = d.argmin(axis=1)
        if (new_labels == labels).all():
            labels = new_labels
            break
        labels = new_labels
        for c in range(k):
            mask = labels == c
            if mask.any():
                centers[c] = pixels[mask].mean(axis=0)
            else:  # re-seed empty cluster with a random point
                centers[c] = pixels[rng.integers(0, n)]
    d = ((pixels[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
    return centers, d.argmin(axis=1)


def analyze_image(image_bytes: bytes, filename: str, out_dir: str):
    """Run all local image analysis. Saves original + thumbnail. Returns a dict."""
    os.makedirs(out_dir, exist_ok=True)
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    img = img.convert("RGB")

    w, h = img.size
    orig_path = os.path.join(out_dir, "photo.jpg")
    img.save(orig_path, "JPEG", quality=88)

    thumb_w = 900
    scale = min(1.0, thumb_w / w)
    thumb = img if scale >= 1.0 else img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    thumb_path = os.path.join(out_dir, "photo_thumb.jpg")
    thumb.save(thumb_path, "JPEG", quality=85)

    # Work at a manageable resolution
    work = img.resize((min(480, w), min(480, h)), Image.LANCZOS)
    arr = np.asarray(work, dtype=np.float32)
    hh, ww = arr.shape[:2]

    # --- Foreground crop: estimate background from border pixels ---
    border = np.concatenate([
        arr[0, :, :], arr[-1, :, :], arr[:, 0, :], arr[:, -1, :]
    ])
    bg = np.median(border, axis=0)
    dist = np.sqrt(((arr - bg[None, None, :]) ** 2).sum(axis=2))
    fg = dist > max(24.0, 0.10 * arr.std())
    if fg.sum() < 0.02 * fg.size:  # mostly solid background — no useful crop
        fg = np.ones_like(fg)

    rows = np.where(fg.any(axis=1))[0]
    cols = np.where(fg.any(axis=0))[0]
    y0, y1 = rows[0], rows[-1]
    x0, x1 = cols[0], cols[-1]
    pad = 2
    y0, x0 = max(0, y0 - pad), max(0, x0 - pad)
    y1, x1 = min(hh - 1, y1 + pad), min(ww - 1, x1 + pad)

    fg_mask = fg[y0:y1 + 1, x0:x1 + 1]
    fg_w = x1 - x0 + 1
    fg_h = y1 - y0 + 1
    aspect = round(fg_w / max(1, fg_h), 3)

    # Bottom structure detection: count foreground runs per row in the lower
    # quarter. Two separate legs => 2 runs; a single hem => 1 run.
    bottom = fg_mask[-max(8, fg_mask.shape[0] // 5):, :]
    run_counts = []
    for row in bottom:
        d = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
        run_counts.append(int((d == 1).sum()))
    bottom_gap = bool(len(run_counts) and float(np.median(run_counts)) >= 2)

    # Row-width profile of the foreground (top vs mid vs bottom width)
    row_widths = fg_mask.sum(axis=1)
    n_rows = max(1, row_widths.size)
    top_w = row_widths[: max(1, n_rows // 4)].mean()
    mid_w = row_widths[n_rows // 3: 2 * n_rows // 3].mean()
    bot_w = row_widths[-max(1, n_rows // 4):].mean()

    # --- Colour palette via k-means on foreground pixels (fallback: whole image) ---
    pix = arr[y0:y1 + 1, x0:x1 + 1].reshape(-1, 3)
    m = fg_mask.reshape(-1)
    if m.sum() > 200:
        pix = pix[m]
    pix = pix[:: max(1, pix.shape[0] // 12000)]
    centers, labels = _kmeans(pix, k=6)
    counts = np.bincount(labels, minlength=len(centers))
    order = np.argsort(-counts)

    # Merge near-duplicate clusters (e.g. heather textures) so the palette
    # shows genuinely distinct colours.
    merged = []
    for c in order:
        cov = counts[c] / max(1, labels.size)
        if cov < 0.02:
            continue
        rgb = centers[c].astype(np.float64)
        for m in merged:
            if float(np.linalg.norm(rgb - m["rgb"])) < 24:
                tot = m["cov"] + cov
                m["rgb"] = (m["rgb"] * m["cov"] + rgb * cov) / tot
                m["cov"] = tot
                break
        else:
            merged.append({"rgb": rgb, "cov": float(cov)})
    total = sum(m["cov"] for m in merged) or 1.0
    merged.sort(key=lambda m: -m["cov"])

    swatches = []
    for m in merged[:4]:
        rgb = [int(v) for v in m["rgb"].round()]
        hexv = "#%02x%02x%02x" % tuple(rgb)
        name = name_color(rgb)
        swatches.append({
            "hex": hexv,
            "rgb": rgb,
            "name": name,
            "pantone": PANTONE_SUGGESTED.get(name, "Match against Pantone TCX guide"),
            "coverage": round(m["cov"] / total * 100, 1),
        })
    if not swatches:
        rgb = [int(v) for v in arr.reshape(-1, 3).mean(axis=0)]
        swatches.append({
            "hex": "#%02x%02x%02x" % tuple(rgb), "rgb": rgb,
            "name": name_color(rgb), "pantone": "Match against Pantone TCX guide",
            "coverage": 100.0,
        })

    luminance = (0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2])
    contrast = float(arr.std())
    dominant_sat = float(np.abs(arr.max(axis=2) - arr.min(axis=2)).mean())

    crop_path = os.path.join(out_dir, "crop.jpg")
    work.crop((x0, y0, x1 + 1, y1 + 1)).save(crop_path, "JPEG", quality=85)

    return {
        "filename": filename,
        "size": [w, h],
        "original": orig_path,
        "thumb": thumb_path,
        "crop": crop_path,
        "swatches": swatches,
        "aspect": aspect,
        "bottom_gap": bool(bottom_gap),
        "profile": {
            "top": round(float(top_w) / max(1, fg_w), 3),
            "mid": round(float(mid_w) / max(1, fg_w), 3),
            "bottom": round(float(bot_w) / max(1, fg_w), 3),
        },
        "brightness": round(float(luminance.mean()) / 255.0, 3),
        "contrast": round(contrast / 255.0, 3),
        "saturation": round(dominant_sat / 255.0, 3),
    }
