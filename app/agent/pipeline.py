"""The tech-pack agent pipeline.

Steps (streamed to the UI as they run):
  1. ingest    — save the upload, run local image analysis
  2. classify  — garment category (user selection or heuristic)
  3. vision    — optional AI-vision enrichment (needs an API key)
  4. specs     — build the 10-section specification from the knowledge base
  5. drawings  — generate the flat technical sketch (SVG)
  6. reports   — render PDF + Markdown exports
"""
import datetime as _dt
import json
import os
import random

from . import classifier, image_analyzer, vision
from .knowledge import (
    APPROVALS, ARTWORK_REQUIREMENTS, ARTWORK_SPEC, CATEGORIES, DEFAULT_CATEGORY,
    PACKAGING_BASE, SAMPLE_FEEDBACK_ROWS, SIZE_LADDER, STITCH_SPECS, THREAD_SPEC,
    size_table,
)

DEFAULT_STYLE_NAMES = {
    "tshirt": "Crew Neck Tee", "top": "Long Sleeve Top", "shirt": "Oxford Shirt",
    "hoodie": "Fleece Hoodie", "jacket": "Zip Jacket", "pants": "5-Pocket Jean",
    "shorts": "Chino Shorts", "dress": "A-Line Dress", "skirt": "A-Line Skirt",
}


def auto_season(today=None):
    today = today or _dt.date.today()
    m, y = today.month, today.year % 100
    if m in (7, 8, 9, 10):
        return f"SS{(y + 1) % 100:02d}"
    if m in (11, 12):
        return f"FW{(y + 1) % 100:02d}"
    if m in (1, 2, 3):
        return f"FW{y:02d}"
    return f"SS{y:02d}"


def parse_size_range(raw, default="XS-XL"):
    raw = (raw or default).strip().upper().replace("–", "-").replace(" ", "")
    if "-" not in raw:
        raw = default
    lo, hi = raw.split("-", 1)
    if lo not in SIZE_LADDER or hi not in SIZE_LADDER:
        lo, hi = "XS", "XL"
    i0, i1 = SIZE_LADDER.index(lo), SIZE_LADDER.index(hi)
    if i0 > i1:
        i0, i1 = i1, i0
    return SIZE_LADDER[i0:i1 + 1], f"{lo}-{hi}"


def _fmt(cm, units):
    if units == "in":
        v = cm / 2.54
        return f"{v:.2f} in"
    v = round(cm, 1)
    return f"{v:.0f} cm" if v == int(v) else f"{v:.1f} cm"


def _fmt_num(cm, units):
    if units == "in":
        return round(cm / 2.54, 2)
    v = round(cm, 1)
    return int(v) if v == int(v) else v


def build_pack(ctx):
    """Assemble the full tech pack dict from pipeline context."""
    cat = CATEGORIES[ctx["category"]]
    sizes, size_range = ctx["sizes"], ctx["size_range"]
    units = ctx["units"]
    sample_size = ctx["sample_size"]
    i_sample = sizes.index(sample_size)
    today = ctx["date"]
    swatches = ctx["analysis"]["swatches"]
    primary = swatches[0]
    colorway = f"{primary['name']} ({primary['hex']})"
    if len(swatches) > 1:
        colorway += f" + {swatches[1]['name']}"

    season = ctx.get("season") or auto_season(today)
    style_code = ctx.get("style_code") or (
        f"{cat['code_prefix']}-{season}-{random.randint(100, 999)}")
    style_name = ctx.get("style_name") or DEFAULT_STYLE_NAMES[ctx["category"]]

    notes = []
    if ctx.get("classify_reason"):
        notes.append(f"Garment type: {ctx['category']} "
                     f"(auto-detected, confidence {ctx.get('confidence', 'low')}: "
                     f"{ctx['classify_reason']}) — please verify.")
    else:
        notes.append(f"Garment type confirmed by user: {cat['label']}.")
    notes.append("Values are standard production baselines; verify every "
                 "measurement, trim and colour against the approved sample.")
    if ctx.get("ai") and ctx["ai"].get("observations"):
        notes.append(f"AI observations contributed ({ctx['ai'].get('provider')}).")

    # --- Section 5: measurements (finished garment, sample size) ---
    m_rows = []
    for (key, name, base, step, tol_s, tol_l, how) in cat["measurements"]:
        vals = size_table(base, step, sizes)
        m_rows.append([
            name, how, _fmt(vals[i_sample], units),
            f"±{_fmt(tol_s, units)} (XS–M) · ±{_fmt(tol_l, units)} (L+)",
        ])

    # --- Section 6: grading table ---
    g_rows = []
    for (key, name, base, step, tol_s, tol_l, how) in cat["measurements"]:
        vals = size_table(base, step, sizes)
        g_rows.append([name] + [_fmt_num(v, units) for v in vals] +
                      [_fmt_num(step, units) if step else 0])

    # --- Section 3: fabric ---
    f = cat["fabric"]
    fabric_rows = [
        ["Fabric type", f["type"]],
        ["Fibre composition", f["composition"]],
        ["Weight", f["weight"]],
        ["Colour", f"{colorway} — match against approved lab dip"],
        ["Finish / wash", f["finish"]],
        ["Lining", f["lining"]],
        ["Colorfastness", f["colorfastness"]],
        ["Shrinkage", f["shrinkage"]],
        ["Supplier reference", f["supplier"]],
        ["Fabric consumption", cat["consumption"]],
    ]

    # --- Section 8: colours ---
    roles = ["Primary", "Secondary", "Accent / trim", "Accent / trim"]
    col_rows = []
    for i, sw in enumerate(swatches[:4]):
        col_rows.append([
            roles[i] if i < len(roles) else "Detail",
            sw["name"], sw["hex"], f"{sw['coverage']}%", sw["pantone"],
        ])

    pack = {
        "meta": {
            "job_id": ctx["job_id"],
            "created_at": _dt.datetime.now().isoformat(timespec="seconds"),
            "image_file": ctx["analysis"]["filename"],
            "image_size": ctx["analysis"]["size"],
            "units": units,
            "agent": "Tech Pack Agent v1.0",
        },
        "style": {
            "brand": ctx.get("brand") or "Brand (TBC)",
            "style_name": style_name,
            "style_code": style_code,
            "season": season,
            "sample_size": sample_size,
            "size_range": size_range,
            "date": today.isoformat(),
            "version": ctx.get("version") or "1.0",
            "garment": cat["label"],
            "colourway": colorway,
            "notes": notes,
        },
        "drawings": {
            "flat": cat["flat"],
            "flat_title": "Front flat sketch — standard construction & measurement points",
            "details": cat["details"],
            "photo_note": "Reference photo as uploaded. Final technical drawings to be "
                          "redrawn and verified against the approved sample.",
        },
        "fabric": {"rows": fabric_rows},
        "bom": {"rows": cat["bom"]},
        "measurements": {
            "rows": m_rows,
            "note": f"Finished-garment (flat) measurements at size {sample_size}. "
                    "Measurement positions shown on the front flat sketch (Section 2). "
                    "Tolerance = acceptable variation on the finished garment.",
        },
        "grading": {
            "sizes": sizes,
            "rows": g_rows,
            "rules": f"Full-size step grading, base size {sample_size}. Step column = change "
                     "per full size. Grade outwards from the base size; confirm final size "
                     "set on the approved fit sample before bulk production.",
        },
        "construction": {
            "rows": cat["construction"],
            "thread": THREAD_SPEC,
            "stitches": STITCH_SPECS,
        },
        "colours": {
            "swatches": swatches[:4],
            "colorway_rows": col_rows,
            "artwork": ARTWORK_SPEC,
            "requirements": ARTWORK_REQUIREMENTS,
        },
        "labels_packaging": {"rows": PACKAGING_BASE},
        "sample_feedback": {
            "rows": SAMPLE_FEEDBACK_ROWS,
            "revisions": [[ctx.get("version") or "1.0", today.isoformat(),
                           "Tech Pack Agent", "Initial tech pack generated from sample photo"]],
            "approvals": APPROVALS,
        },
        "ai": ctx.get("ai"),
    }
    return pack


STEPS = [
    ("ingest", "Saving photo & analysing image (colour, structure)"),
    ("classify", "Identifying garment type"),
    ("vision", "AI vision pass (optional)"),
    ("specs", "Building specifications — fabric, BOM, measurements, grading, construction"),
    ("drawings", "Generating flat technical sketch"),
    ("reports", "Rendering PDF & Markdown reports"),
]


def run_generation(form, image_bytes, job_id, jobs_dir):
    """Generator: yields SSE-ready (event, payload) tuples. Last event: ('done', {...})."""
    from ..report import flat as flat_mod
    from ..report import markdown as md_mod
    from ..report import pdf as pdf_mod

    def sse(event, data):
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    job_dir = os.path.join(jobs_dir, job_id)
    os.makedirs(job_dir, exist_ok=True)

    today = form.get("date") or _dt.date.today().isoformat()
    today = _dt.date.fromisoformat(today)

    def emit(sid, status, detail=""):
        label = dict(STEPS)[sid]
        yield sse("step", {"id": sid, "label": label, "status": status, "detail": detail})

    # 1 — ingest -------------------------------------------------------
    yield from emit("ingest", "running")
    analysis = image_analyzer.analyze_image(image_bytes, form.get("filename", "photo.jpg"), job_dir)
    yield from emit("ingest", "done",
                    f"{len(analysis['swatches'])} colours found · "
                    f"image {analysis['size'][0]}×{analysis['size'][1]}")

    # 2 — classify -----------------------------------------------------
    yield from emit("classify", "running")
    user_cat = (form.get("garment_type") or "auto").lower()
    if user_cat in CATEGORIES:
        category, confidence, reason = user_cat, "confirmed", "user selected"
    else:
        category, confidence, reason = classifier.classify(analysis)
        category = category if category in CATEGORIES else DEFAULT_CATEGORY
    yield from emit("classify", "done",
                    f"{CATEGORIES[category]['label']} ({confidence})")

    # 3 — optional AI vision -------------------------------------------
    yield from emit("vision", "running")
    ai, ai_note = None, None
    if (form.get("use_ai", "1") or "1") in ("1", "true"):
        ai, ai_note = vision.vision_observe(analysis["thumb"])
        # Let the AI override the auto-guess when it is confident
        if (ai and user_cat == "auto" and ai.get("garment_type") in CATEGORIES
                and float(ai.get("confidence", 0) or 0) >= 0.75):
            category = ai["garment_type"]
            reason = (f"AI vision ({ai_note}), confidence "
                      f"{ai.get('confidence')}")
            confidence = "ai"
    ai_payload = {"observations": ai, "provider": ai_note} if ai else {"observations": None, "provider": ai_note}
    yield from emit("vision", "done", ai_note or "")

    # 4 — specs ----------------------------------------------------------
    yield from emit("specs", "running")
    sizes, size_range = parse_size_range(form.get("size_range"))
    sample_size = form.get("sample_size") or "M"
    if sample_size not in sizes:
        sample_size = sizes[len(sizes) // 2]
    ctx = {
        "job_id": job_id,
        "analysis": analysis,
        "category": category,
        "confidence": confidence,
        "classify_reason": reason,
        "sizes": sizes,
        "size_range": size_range,
        "units": form.get("units") or "cm",
        "sample_size": sample_size,
        "brand": form.get("brand"),
        "style_name": form.get("style_name"),
        "style_code": form.get("style_code"),
        "season": form.get("season"),
        "version": form.get("version") or "1.0",
        "date": today,
        "ai": ai_payload,
    }
    pack = build_pack(ctx)
    pack_path = os.path.join(job_dir, "pack.json")
    with open(pack_path, "w") as fh:
        json.dump(pack, fh, indent=2)
    yield from emit("specs", "done", f"10 sections built for {size_range}")

    # 5 — drawings -------------------------------------------------------
    yield from emit("drawings", "running")
    svg = flat_mod.render_svg(CATEGORIES[category]["flat"])
    with open(os.path.join(job_dir, "flat.svg"), "w") as fh:
        fh.write(svg)
    yield from emit("drawings", "done", f"flat sketch: {category}")

    # 6 — reports ----------------------------------------------------------
    yield from emit("reports", "running")
    pdf_path = pdf_mod.generate_pdf(pack, job_dir, analysis["thumb"])
    md_path = os.path.join(job_dir, "techpack.md")
    with open(md_path, "w") as fh:
        fh.write(md_mod.generate_md(pack))
    yield from emit("reports", "done", "PDF + Markdown ready")

    yield sse("done", {
        "job_id": job_id,
        "pack": pack,
        "files": {
            "pdf": f"/api/jobs/{job_id}/techpack.pdf",
            "md": f"/api/jobs/{job_id}/techpack.md",
            "json": f"/api/jobs/{job_id}/pack.json",
            "image": f"/api/jobs/{job_id}/photo",
            "flat": f"/api/jobs/{job_id}/flat.svg",
        },
    })
